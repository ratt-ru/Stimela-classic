import os
import sys

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

msname = jdict.pop("msname")

if isinstance(msname, (list, tuple)):
    mslist = " ".join(["%s/%s"%(MSDIR, ms) for ms in msname])
    vis = msname[0]
else:
    vis = msname
    mslist = MSDIR + "/" + msname

mask = jdict.pop("mask")
for place in ["/input", "/output", "/msdir"]:
    if mask.startswith(place):
        pass
    else:
        mask = INPUT + "/" + mask
        break

args = ["--mask %s"%mask]
stats = jdict.pop("stats", True)

if stats:
    args += ["-s"]

args += ["--%s %s"%(a,b) for a,b in jdict.iteritems()]

utils.xrun("mask_ms.py", args + [mslist])
