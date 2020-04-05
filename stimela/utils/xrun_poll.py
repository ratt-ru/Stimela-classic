import select, traceback, subprocess, errno, re, time

DEBUG = 0
from . import StimelaCabRuntimeError

class Poller(object):
    """Poller class. Poor man's select.poll(). Damn you OS/X and your select.poll will-you-won'y-you bollocks"""
    def __init__ (self, log):
        self.fdlabels = {}
        self.log = log

    def register_file(self, fobj, label):
        self.fdlabels[fobj.fileno()] = label, fobj

    def register_process(self, po, label_stdout='stdout', label_stderr='stderr'):
        self.fdlabels[po.stdout.fileno()] = label_stdout, po.stdout
        self.fdlabels[po.stderr.fileno()] = label_stderr, po.stderr

    def poll(self, timeout=5, verbose=False):
        while True:
            try:
                to_read, _, _ = select.select(self.fdlabels.keys(), [], [], timeout)
                self.log.debug("poll(): ready to read: {}".format(to_read))
                # return on success or timeout
                return [self.fdlabels[fd] for fd in to_read]
            except (select.error, IOError) as ioerr:
                if verbose:
                    self.log.debug("poll() exception: {}".format(traceback.format_exc()))
                if hasattr(ioerr, 'args'):
                    err = ioerr.args[0]  # py2
                else:
                    err = ioerr.errno    # py3
                # catch interrupted system call -- return if we have a timeout, else
                # loop again
                if err == errno.EINTR:
                    if timeout is not None:
                        if verbose:
                            self.log.debug("poll(): returning")
                        return []
                    if verbose:
                        self.log.debug("poll(): retrying")
                else:
                    raise

    def unregister_file(self, fobj):
        if fobj.fileno() in self.fdlabels:
            del self.fdlabels[fobj.fileno()]

    def __contains__(self, fobj):
        return fobj.fileno() in self.fdlabels


def _remove_ctrls(msg):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', msg)


def xrun_nolog(command):
    try:
        status = subprocess.call(command, shell=True)

    except KeyboardInterrupt:
        print("Ctrl+C caught")
        status = 1

    except Exception as exc:
        traceback.print_exc()
        print("Exception caught: {}".format(str(exc)))
        status = 1

    return status

def xrun(command, options, log=None, logfile=None, timeout=-1, kill_callback=None):

    command_name = command

    # this part could be inside the container
    command = " ".join([command] + list(map(str, options)))

    if not log:
        return xrun_nolog(command)

    # this part is never inside the container
    import stimela

    log = log or stimela.logger()

    log.info("running " + command)

    start_time = time.time()

    proc = subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            bufsize=1, universal_newlines=True, shell=True)

    poller = Poller(log=log)
    poller.register_process(proc)

    proc_running = True

    try:
        while proc_running and poller.fdlabels:
            fdlist = poller.poll(verbose=DEBUG>0)
            for fname, fobj in fdlist:
                try:
                    line = fobj.readline()
                except EOFError:
                    line = b''
                empty_line = not line
                line = (line.decode('utf-8') if type(line) is bytes else line).rstrip()
                # break out if process closes
                if empty_line:
                    poller.unregister_file(fobj)
                    if proc.stdout not in poller and proc.stderr not in poller:
                        log.debug("The {} process has exited".format(command))
                        proc_running = None
                        break
                    continue
                # dispatch output to log
                line = _remove_ctrls(line)
                # the extra attributes are filtered by e.g. the CARACal logger
                if fobj is proc.stderr:
                    log.warning(line, extra=dict(stimela_subprocess_output=(command_name, "stderr")))
                else:
                    log.info(line, extra=dict(stimela_subprocess_output=(command_name, "stdout")))
            if timeout > 0 and time.time() > start_time + timeout:
                log.error("timeout, killing {} process".format(command))
                kill_callback() if callable(kill_callback) else proc.kill()
                proc_running = False

        proc.wait()
        status = proc.returncode

    except SystemExit as exc:
        log.error("{} has exited with code {}".format(command, exc.code))
        proc.wait()
        status = exc.code
        raise StimelaCabRuntimeError('{}: SystemExit with code {}'.format(command_name, status))

    except KeyboardInterrupt:
        log.error("Ctrl+C caught")
        proc.wait()
        raise StimelaCabRuntimeError('{} interrupted with Ctrl+C'.format(command_name))

    except Exception as exc:
        traceback.print_exc()
        log.error("Exception caught: {}".format(str(exc)))
        proc.wait()
        raise StimelaCabRuntimeError("{} throws exception '{}'".format(command_name, str(exc)))

    if status:
        raise StimelaCabRuntimeError("{} returns error code {}".format(command_name, status))
    
    return status
    