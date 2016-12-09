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
outvis = options.pop("output_msname")
options["vis"] = MSDIR + "/" + vis
options["outputvis"] = MSDIR + "/" + outvis

utils.icasa("split", **options)
