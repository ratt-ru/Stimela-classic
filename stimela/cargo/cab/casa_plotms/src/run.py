import os
import sys

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

options = utils.readJson(CONFIG)
vis = options.pop("msname")
options["vis"] = MSDIR + "/" + vis
plotfile = options.pop("plotfile")

options["plotfile"] = utils.substitute_globals(plotfile) or OUTPUT +"/"+plotfile
options["showgui"] = False
utils.icasa("plotms", **options)
