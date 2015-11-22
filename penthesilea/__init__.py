import os
import otrera

__version__ = otrera.__version__

ekhaya = os.path.dirname(__file__)
STABLE_TAG = "stable.11.15"

# Path to base images
PENTHESILEA_BASE_PATH = "{:s}/base".format(ekhaya)

# Path to executor images
PENTHESILEA_ARES_PATH = "{:s}/ares".format(ekhaya)

# Path to native data products
PENTHESILEA_DATA = "{:s}/data".format(ekhaya)

# Path to config templates
PENTHESILEA_CONFIG_TEMPLATES = "{:s}/configs".format(ekhaya)
