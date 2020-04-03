import os
import sys
import inspect
import pkg_resources
import logging

try:
    __version__ = pkg_resources.require("stimela")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"

# Get to know user
USER = os.environ["USER"]
UID = os.getuid()
GID = os.getgid()

root = os.path.dirname(__file__)

CAB_PATH = os.path.join(root, "cargo/cab")
BASE_PATH = os.path.join(root, "cargo/base")

# Set up logging infrastructure
LOG_HOME = os.path.expanduser("~/.stimela")
# This is is the default log file. It logs stimela images, containers and processes
LOG_FILE = "{0:s}/stimela_logfile.json".format(LOG_HOME)

GLOBALS = {'foo': 'bar'}
del GLOBALS['foo']

def register_globals():
    frame = inspect.currentframe().f_back
    frame.f_globals.update(GLOBALS)

# Get base images
# All base images must be on dockerhub
BASE = os.listdir(BASE_PATH)
CAB = list()

for item in os.listdir(CAB_PATH):
    try:
        # These files must exist for a cab image to be valid
        ls_cabdir = os.listdir('{0}/{1}'.format(CAB_PATH, item))
        dockerfile = 'Dockerfile' in ls_cabdir
        paramfile = 'parameters.json' in ls_cabdir
        srcdir = 'src' in ls_cabdir
    except OSError:
        continue
    if dockerfile and paramfile and srcdir:
        CAB.append(item)


class SelectiveFormatter(logging.Formatter):
    """Selective formatter. if condition(record) is True, invokes other formatter"""
    def __init__(self, fmt=None, datefmt=None, style='%', condition=None, other=None):
        super(SelectiveFormatter, self).__init__(fmt, datefmt, style)
        self._condition = condition
        self._other = other

    def format(self, record):
        if self._condition and self._other and self._condition(record):
            return self._other.format(record)
        return super(SelectiveFormatter, self).format(record)


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


_logger = None

log_console_handler = log_formatter = None

def logger(name="STIMELA", propagate=False, console=True,
           fmt="{asctime} {name} {levelname}: {message}",
           sub_fmt="{message}",
           datefmt="%Y-%m-%d %H:%M:%S"):
    """Returns the global Stimela logger (initializing if not already done so, with the given values)"""
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.propagate = propagate

        global log_console_handler, log_formatter

        log_formatter = SelectiveFormatter(fmt, datefmt, style="{",
                                           condition=lambda rec:hasattr(rec, 'subprocess'),
                                           other=logging.Formatter(sub_fmt, datefmt, style="{"))

        if console:
            log_console_handler = MultiplexingHandler()
            log_console_handler.setFormatter(log_formatter)
            log_console_handler.setLevel(logging.DEBUG)
            _logger.addHandler(log_console_handler)

    return _logger


from stimela.recipe import Recipe
