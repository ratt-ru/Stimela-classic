# -*- coding: future_fstrings -*-
import os, sys, re
import inspect
import pkg_resources
import logging
from logging import StreamHandler
from typing import Union, Optional
from pathlib import Path
from omegaconf import OmegaConf

try:
    __version__ = pkg_resources.require("stimela")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"

CONFIG = None

# Get to know user
USER = os.environ["USER"]
UID = os.getuid()
GID = os.getgid()
CAB_USERNAME = re.sub('[^0-9a-zA-Z]+', '_', USER).lower() 

root = os.path.dirname(__file__)

CAB_PATH = os.path.join(root, "cargo/cab")
BASE_PATH = os.path.join(root, "cargo/base")

# Set up logging infrastructure
LOG_HOME = os.path.expanduser("~/.stimela")
# make sure directory exists
Path(LOG_HOME).mkdir(exist_ok=True)
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
    itempath = os.path.join(CAB_PATH, item)
    if os.path.isdir(itempath):
        try:
            # These files must exist for a cab image to be valid
            ls_cabdir = os.listdir(itempath)
            paramfile = 'parameters.json' in ls_cabdir
            srcdir = 'src' in ls_cabdir
        except OSError:
            continue
        if paramfile and srcdir:
            CAB.append(item)


from .stimelogging import logger

from stimela.kitchen.recipe import Recipe

