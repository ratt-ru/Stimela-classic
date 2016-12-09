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

mask = utils.substitute_globals(mask) or INPUT + "/" + mask

args = ["--mask %s"%mask]

args += ["--%s %s"%(a, "" if isinstance(b, bool) else b) for a,b in jdict.iteritems()]

utils.xrun("mask_ms.py", args + [mslist])
