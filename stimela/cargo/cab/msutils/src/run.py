import sys
import os
from MSUtils import msutils

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)
cab_dict_update = utils.cab_dict_update

msname = jdict.pop("msname")
msname = MSDIR + "/" + msname

function = jdict.pop("command")

run_func = getattr(msutils, function, None)
if run_func is None:
    raise RuntimeError("Function %s is not part of MSUtils"%function)

jdict["msname"] = msname

run_func(**jdict)
