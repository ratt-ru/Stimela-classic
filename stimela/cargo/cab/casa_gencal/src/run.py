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
gains = options.pop("gaintable", [])

caltable = utils.substitute_globals(caltable) or OUTPUT+"/"+caltable
for i,gain in enumerate(gains):
    gains[i] = utils.substitute_globals(gain) or INPUT+"/"+gain

options["caltable"] = caltable
utils.icasa("gencal", **options)
