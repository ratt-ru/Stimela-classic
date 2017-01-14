import os
import sys

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

options = utils.readJson(CONFIG)
vis = options.pop("vis")
visout = options.pop("outputvis")
options["vis"] = MSDIR + "/" + vis
options["outputvis"] = MSDIR + "/" + visout
utils.icasa("fixvis", **options)
