import os
import sys
import inspect
import pkg_resources

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

from stimela.recipe import Recipe
