import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

msnames = jdict.pop("msname")

if isinstance(msnames, (str, unicode)):
    msnames = [msnames]

msname = [ "%s/%s"%(MSDIR, ms) for ms in msnames ]

export = jdict.pop("export", None)
export = "--s %s/%s"%(INPUT, export) if export else ""
 
flag_cmd = ["--%s %s"%(a, "" if isinstance(b, bool) else b) for a,b in jdict.iteritems()] or [""]


def flagms(ms):
    utils.xrun("flag-ms.py", flag_cmd+[export, ms])

ncpu = jdict.get("ncpu", 1)

utils.pper(msname, flagms, ncpu)
