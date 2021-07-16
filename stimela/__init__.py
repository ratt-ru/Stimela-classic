# -*- coding: future_fstrings -*-
import os
import sys
import inspect
import pkg_resources
import logging
from logging import StreamHandler
import re
from pathlib import Path

try:
    __version__ = pkg_resources.require("stimela")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"

# Get to know user
USER = os.environ["USER"]
UID = os.getuid()
GID = os.getgid()
CAB_USERNAME = re.sub('[^0-9a-zA-Z]+', '_', USER).lower() 

root = os.path.dirname(__file__)

CAB_PATH = os.path.join(root, "cargo/cab")
BASE_PATH = os.path.join(root, "cargo/base")


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
        paramfile = 'parameters.json' in ls_cabdir
        srcdir = 'src' in ls_cabdir
    except OSError:
        continue
    if paramfile and srcdir:
        CAB.append(item)


_logger = None

from .utils.logger import SelectiveFormatter, ColorizingFormatter, ConsoleColors, MultiplexingHandler

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
        _logger.setLevel(getattr(logging, loglevel))
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
                log_console_handler = StreamHandler(stream=sys.stdout)
            else:  
                log_console_handler = MultiplexingHandler()
            log_console_handler.setFormatter(log_formatter)
            log_console_handler.setLevel(getattr(logging, loglevel))
            _logger.addHandler(log_console_handler)

    return _logger

from stimela.recipe import Recipe

