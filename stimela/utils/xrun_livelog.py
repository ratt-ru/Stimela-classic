import sys, os, codecs, time, hashlib, subprocess

from threading import Event, Thread

from . import StimelaCabRuntimeError

DEBUG = False
INTERRUPT_TIME = 2.0  # seconds -- do not want to constantly interrupt the child process
LIVELOG_TIME = 0.1



def xrun(command, options, log=None, _log_container_as_started=False, logfile=None, timeout=-1, kill_callback=None):
    """
        Run something on command line.

        Example: _run("ls", ["-lrt", "../"])
    """
    if "LOGFILE" in os.environ and logfile is None:
        logfile = os.environ["LOGFILE"] # superceed if not set

    # skip lines from previous log files
    if logfile is not None and os.path.exists(logfile):
        with codecs.open(logfile, "r", encoding="UTF-8",
                         errors="ignore", buffering=0) as foutlog:
            lines = foutlog.readlines()
            prior_log_bytes_read = foutlog.tell()
    else: # not existant, create
        prior_log_bytes_read = 0
        if logfile is not None and not os.path.exists(logfile):
            with codecs.open(logfile, "w+", encoding="UTF-8",
                             errors="ignore", buffering=0) as foutlog:
                pass

    cmd = " ".join([command] + list(map(str, options)))

    def _remove_ctrls(msg):
        import re
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', msg)

    def _print_info(msg, loglevel="INFO"):
        if msg is None:
            return
        msg = _remove_ctrls(msg)
        if msg.strip() == "": return
        if log:
            try:
                getattr(log, loglevel.lower())(msg.rstrip('\n'))
            except UnicodeError:
                log.warn("Log contains unicode and will not be printed")
        else:
            try:
                print(msg),
            except UnicodeError:
                print("Log contains unicode and will not be printed")

    def _print_warn(msg):
        if msg is None:
            return
        msg = _remove_ctrls(msg)
        if msg.strip() == "": return
        if log:
            try:
                log.info(msg.rstrip('\n'))
            except UnicodeError:
                log.warn("Log contains unicode and will not be printed")
        else:
            try:
                print(msg),
            except UnicodeError:
                print("Log contains unicode and will not be printed")


    _print_info(u"Running: {0:s}".format(cmd), loglevel="INFO")

    sys.stdout.flush()
    starttime = time.time()
    process = p = None
    stop_log_printer = Event()

    try:
        foutname = os.path.join("/tmp", "stimela_output_{0:s}_{1:f}".format(
            hashlib.md5(cmd.encode('utf-8')).hexdigest(), starttime))


        p = process = subprocess.Popen(cmd,
                                       shell=True)
        kill_callback = kill_callback or p.kill

        def clock_killer(p):
            while process.poll() is None and (timeout >= 0):
                currenttime = time.time()
                if (currenttime - starttime < timeout):
                    DEBUG and _print_warn(u"Clock Reaper: has been running for {0:f}, must finish in {1:f}".format(
                        currenttime - starttime, timeout))
                else:
                    _print_warn(
                        u"Clock Reaper: Timeout reached for '{0:s}'... sending the KILL signal".format(cmd))
                    kill_callback()
                time.sleep(INTERRUPT_TIME)

        def log_reader(logfile, stop_event):
            bytes_read = prior_log_bytes_read # skip any previous runs' output
            while not stop_event.isSet():
                if logfile is not None and os.path.exists(logfile):
                    with codecs.open(logfile, "r", encoding="UTF-8",
                                     errors="ignore", buffering=0) as foutlog:
                        foutlog.seek(bytes_read, 0)
                        lines = foutlog.readlines()
                        bytes_read = foutlog.tell()
                        for line in lines:
                            line and _print_info(line)
                time.sleep(LIVELOG_TIME) # wait for the log to go to disk

        Thread(target=clock_killer, args=tuple([p])).start()
        if log is not None:
            # crucial - child process should not write to stdout unless it is
            # the container process itself
            Thread(target=log_reader, args=tuple([logfile, stop_log_printer])).start()


        while (process.poll() is None):
            currenttime = time.time()
            DEBUG and _print_info(
                u"God mode on: has been running for {0:f}".format(currenttime - starttime))
            # this is probably not ideal as it interrupts the process every few seconds,
            time.sleep(INTERRUPT_TIME)
            # check whether there is an alternative with a callback

        assert hasattr(
            process, "returncode"), "No returncode after termination!"
    finally:
        stop_log_printer.set()
        if (process is not None) and process.returncode:
            raise StimelaCabRuntimeError(
                '%s: returns errr code %d' % (command, process.returncode))

