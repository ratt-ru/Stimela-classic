import os
import otrera

__version__ = otrera.__version__

ekhaya = __path__[0]
STABLE_TAG = "stable.11.15"

# Path to base images
PENTHESILEA_BASE_PATH = "{:s}/base".format(ekhaya)

# Path to executor images
PENTHESILEA_ARES_PATH = "{:s}/ares".format(ekhaya)

# Path to native data products
PENTHESILEA_DATA = "{:s}/data".format(ekhaya)

# Path to config templates
PENTHESILEA_CONFIG_TEMPLATES = configs = "{:s}/configs".format(ekhaya)

