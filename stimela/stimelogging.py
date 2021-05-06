import sys, os.path, re
import logging
from typing import Optional, Dict, Any, Union

class MultiplexingHandler(logging.Handler):
    """handler to send INFO and below to stdout, everything above to stderr"""
    def __init__(self, info_stream=sys.stdout, err_stream=sys.stderr):
        super(MultiplexingHandler, self).__init__()
        self.info_handler = logging.StreamHandler(info_stream)
        self.err_handler = logging.StreamHandler(err_stream)
        self.multiplex = True

    def emit(self, record):
        handler = self.err_handler if record.levelno > logging.INFO and self.multiplex else self.info_handler
        handler.emit(record)
        # ignore broken pipes, this often happens when cleaning up and exiting
        try:
            handler.flush()
        except BrokenPipeError:
            pass

    def flush(self):
        try:
            self.err_handler.flush()
            self.info_handler.flush()
        except BrokenPipeError:
            pass

    def close(self):
        self.err_handler.close()
        self.info_handler.close()

    def setFormatter(self, fmt):
        self.err_handler.setFormatter(fmt)
        self.info_handler.setFormatter(fmt)

class ConsoleColors():
    WARNING = '\033[93m' if sys.stdin.isatty() else ''
    ERROR   = '\033[91m' if sys.stdin.isatty() else ''
    BOLD    = '\033[1m'  if sys.stdin.isatty() else ''
    DIM     = '\033[2m'  if sys.stdin.isatty() else ''
    GREEN   = '\033[92m' if sys.stdin.isatty() else ''
    ENDC    = '\033[0m'  if sys.stdin.isatty() else ''

    BEGIN = "<COLORIZE>"
    END   = "</COLORIZE>"

    @staticmethod
    def colorize(msg, *styles):
        style = "".join(styles)
        return msg.replace(ConsoleColors.BEGIN, style).replace(ConsoleColors.END, ConsoleColors.ENDC if style else "")

class ColorizingFormatter(logging.Formatter):
    """This Formatter inserts color codes into the string according to severity"""
    def __init__(self, fmt=None, datefmt=None, style="%", default_color=None):
        super(ColorizingFormatter, self).__init__(fmt, datefmt, style)
        self._default_color = default_color or ""

    def format(self, record):
        style = ConsoleColors.BOLD if hasattr(record, 'boldface') else ""
        if hasattr(record, 'color'):
            style += getattr(ConsoleColors, record.color or "None", "")
        elif record.levelno >= logging.ERROR:
            style += ConsoleColors.ERROR
        elif record.levelno >= logging.WARNING:
            style += ConsoleColors.WARNING
        return ConsoleColors.colorize(super(ColorizingFormatter, self).format(record), style or self._default_color)


class SelectiveFormatter(logging.Formatter):
    """Selective formatter. if condition(record) is True, invokes other formatter"""
    def __init__(self, default_formatter, dispatch_list):
        self._dispatch_list = dispatch_list
        self._default_formatter = default_formatter

    def format(self, record):
        for condition, formatter in self._dispatch_list:
            if condition(record):
                return formatter.format(record)
        else:
            return self._default_formatter.format(record)


_logger = None
log_console_handler = log_formatter = log_boring_formatter = log_colourful_formatter = None


def is_logger_initialized():
    return _logger is not None


def logger(name="STIMELA", propagate=False, console=True, boring=False,
           fmt="{asctime} {name} {levelname}: {message}",
           col_fmt="{asctime} {name} %s{levelname}: {message}%s"%(ConsoleColors.BEGIN, ConsoleColors.END),
           sub_fmt="# {message}",
           col_sub_fmt="%s# {message}%s"%(ConsoleColors.BEGIN, ConsoleColors.END),
           datefmt="%Y-%m-%d %H:%M:%S", loglevel="INFO"):
    """Returns the global Stimela logger (initializing if not already done so, with the given values)"""
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        if type(loglevel) is str:
            loglevel = getattr(logging, loglevel)
        _logger.setLevel(loglevel)
        _logger.propagate = propagate

        global log_console_handler, log_formatter, log_boring_formatter, log_colourful_formatter

        # this function checks if the log record corresponds to stdout/stderr output from a cab
        def _is_from_subprocess(rec):
            return hasattr(rec, 'stimela_subprocess_output')

        log_boring_formatter = SelectiveFormatter(
                    logging.Formatter(fmt, datefmt, style="{"),
                    [(_is_from_subprocess, logging.Formatter(sub_fmt, datefmt, style="{"))])

        log_colourful_formatter = SelectiveFormatter(
                    ColorizingFormatter(col_fmt, datefmt, style="{"),
                    [(_is_from_subprocess, ColorizingFormatter(fmt=col_sub_fmt, datefmt=datefmt, style="{",
                                                               default_color=ConsoleColors.DIM))])

        log_formatter = log_boring_formatter if boring else log_colourful_formatter

        if console:
            if "SILENT_STDERR" in os.environ and os.environ["SILENT_STDERR"].upper()=="ON":
                log_console_handler = logging.StreamHandler(stream=sys.stdout)
            else:  
                log_console_handler = MultiplexingHandler()
            log_console_handler.setFormatter(log_formatter)
            log_console_handler.setLevel(loglevel)
            _logger.addHandler(log_console_handler)

        import scabha
        scabha.set_logger(_logger)

    return _logger


_logger_file_handlers = {}


def has_file_logger(log: logging.Logger):
    return log.name in _logger_file_handlers


def setup_file_logger(log: logging.Logger, logfile: str, level: Optional[Union[int, str]] = logging.INFO):
    current_logfile, fh = _logger_file_handlers.get(log.name, (None, None))
    
    # does the logger need a new FileHandler created
    if current_logfile != logfile:
        log.debug(f"starting new logfile {logfile} (previous was {current_logfile})")

        # remove old FH if so
        if fh is not None:
            fh.close()
            log.removeHandler(fh)

        # create new one
        logdir = os.path.dirname(logfile)
        if logdir and not os.path.exists(logdir):            
            os.makedirs(logdir)
        
        fh = logging.FileHandler(logfile, 'w', delay=True)
        fh.setFormatter(log_boring_formatter)
        log.addHandler(fh)

        _logger_file_handlers[log.name] = logfile, fh

    # resolve level
    if level is not None:
        if type(level) is str:
            level = getattr(logging, level, logging.INFO)
        fh.setLevel(level)

    return log


def make_filename_substitutions(template: str, subst: Dict[str, Any], default_subst: Optional[Dict[str, Any]]=None):
    # make substitution dict    
    import stimela.config
    default_subst = default_subst or stimela.config.SUBSTITUTIONS
    if subst:
        default_subst = default_subst.copy()
        default_subst.update(**subst)

    return re.sub(r'[^a-zA-Z0-9_./-]', '_', template.format(**default_subst))


def get_logfile_path(template: str, subst: Dict[str, Any]):
    import stimela
    log = logger()

    dirname = os.path.dirname(template) or stimela.CONFIG.opts.log.dir or "."
    basename = f"{stimela.CONFIG.opts.log.prefix}{os.path.basename(template)}{stimela.CONFIG.opts.log.suffix}"
    path = os.path.join(dirname, basename)
    
    # substitute
    try: 
        path = make_filename_substitutions(path, subst)
    except Exception as exc:
        log.error(f"bad substitution in logfile path '{path}': {exc}")
        return None
    
    return path


def update_file_logger(log: logging.Logger, template: str, subst: Dict[str, Any]):
    import stimela

    log_filename = get_logfile_path(template, subst)
    if log_filename is not None:
        setup_file_logger(log, log_filename, stimela.CONFIG.opts.log.level)



