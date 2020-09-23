import select, traceback, subprocess, errno, re, time, logging, os, sys

DEBUG = 0
from . import StimelaCabRuntimeError, StimelaProcessRuntimeError

log = None

def get_stimela_logger():
    """Returns Stimela's logger, or None if no Stimela installed"""
    try:
        import stimela
        return stimela.logger()
    except ImportError:
        return None

def global_logger():
    """Returns Stimela logger if running in stimela, else inits a global logger"""
    global log
    if log is None:
        log = get_stimela_logger()
        if log is None:
            # no stimela => running payload inside a cab -- just use the global logger and make it echo everything to the console
            logging.basicConfig(format="%(message)s", level=logging.INFO, stream=sys.stdout)
            log = logging.getLogger()
    return log

class SelectPoller(object):
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
                    raise ioerr

    def unregister_file(self, fobj):
        if fobj.fileno() in self.fdlabels:
            del self.fdlabels[fobj.fileno()]

    def __contains__(self, fobj):
        return fobj.fileno() in self.fdlabels

class Poller(object):
    """Poller class. Wraps select.poll()."""
    def __init__ (self, log):
        self.fdlabels = {}
        self.log = log
        self._poll = select.poll()

    def register_file(self, fobj, label):
        self.fdlabels[fobj.fileno()] = label, fobj
        self._poll.register(fobj.fileno(), select.POLLIN)

    def register_process(self, po, label_stdout='stdout', label_stderr='stderr'):
        self.fdlabels[po.stdout.fileno()] = label_stdout, po.stdout
        self.fdlabels[po.stderr.fileno()] = label_stderr, po.stderr
        self._poll.register(po.stdout.fileno(), select.POLLIN)
        self._poll.register(po.stderr.fileno(), select.POLLIN)

    def poll(self, timeout=5, verbose=False):
        try:
            to_read = self._poll.poll(timeout*1000)
            if verbose:
                self.log.debug("poll(): ready to read: {}".format(to_read))
            return [self.fdlabels[fd] for (fd, ev) in to_read]
        except Exception:
            if verbose:
                self.log.debug("poll() exception: {}".format(traceback.format_exc()))
            raise

    def unregister_file(self, fobj):
        if fobj.fileno() in self.fdlabels:
            self._poll.unregister(fobj.fileno())
            del self.fdlabels[fobj.fileno()]

    def __contains__(self, fobj):
        return fobj.fileno() in self.fdlabels


def _remove_ctrls(msg):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', msg)


def xrun_nolog(command, name=None):
    log = global_logger()
    name = name or command.split(" ", 1)[0]
    try:
        log.info("# running {}".format(command))
        status = subprocess.call(command, shell=True)

    except KeyboardInterrupt:
        log.error("# {} interrupted by Ctrl+C".format(name))
        raise

    except Exception as exc:
        for line in traceback.format_exc():
            log.error("# {}".format(line.strip()))
        log.error("# {} raised exception: {}".format(name, str(exc)))
        raise

    if status:
        raise StimelaProcessRuntimeError("{} returns error code {}".format(name, status))

    return 0

def xrun(command, options, log=None, logfile=None, env=None, timeout=-1, kill_callback=None, output_wrangler=None):
    command_name = command

    # this part could be inside the container
    command = " ".join([command] + list(map(str, options)))

    log = log or get_stimela_logger()

    if log is None:
        return xrun_nolog(command, name=command_name)

    # this part is never inside the container
    import stimela

    log = log or stimela.logger()

    log.info("running " + command, extra=dict(stimela_subprocess_output=(command_name, "start")))

    start_time = time.time()

    proc = subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env, bufsize=1, universal_newlines=True, shell=True)

    poller = Poller(log=log)
    poller.register_process(proc)

    proc_running = True

    try:
        while proc_running and poller.fdlabels:
            fdlist = poller.poll(verbose=DEBUG>0)
#            print(f"fdlist is {fdlist}")
            for fname, fobj in fdlist:
                try:
                    line = fobj.readline()
                except EOFError:
                    line = b''
#                print("read {} from {}".format(line, fname))
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
                severity = logging.WARNING if fobj is proc.stderr else logging.INFO
                stream_name = "stderr" if fobj is proc.stderr else "stdout"
                # feed through wrangler to adjust severity and content
                if output_wrangler is not None:
                    line, severity = output_wrangler(line, severity, log)
                if line is not None:
                    log.log(severity, line, extra=dict(stimela_subprocess_output=(command_name, stream_name)))
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
        if callable(kill_callback):
            log.warning("Ctrl+C caught: shutting down {} process, please give it a few moments".format(command_name))
            kill_callback() 
            log.info("the {} process was shut down successfully".format(command_name),
                     extra=dict(stimela_subprocess_output=(command_name, "status")))
        else:
            log.warning("Ctrl+C caught, killing {} process".format(command_name))
            proc.kill()
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
    
