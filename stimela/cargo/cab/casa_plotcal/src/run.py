import os
import sys

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

options = utils.readJson(CONFIG)
figfile = options.pop("figfile")
caltable = options.pop("caltable")

options["caltable"] = utils.substitute_globals(caltable) or OUTPUT+"/"+caltable
options["figfile"] = utils.substitute_globals(figfile) or OUTPUT+"/"+figfile


utils.icasa("plotcal", **options)
