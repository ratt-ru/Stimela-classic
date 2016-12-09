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

caltable = options.pop("caltable")
fluxtable = options.pop("fluxtable")

caltable = utils.substitute_globals(caltable) or OUTPUT+"/"+caltable
fluxtable = utils.substitute_globals(fluxtable) or OUTPUT+"/"+fluxtable

options["caltable"] = caltable
options["fluxtable"] = fluxtable

utils.icasa("fluxscale", **options)
