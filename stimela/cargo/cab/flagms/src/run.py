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
ncpu = jdict.pop("ncpu", 1)

export = jdict.pop("export", None)
if export:
    export = utils.substitute_globals(export) or INPUT + "/" + export
    export = "--export %s"%export
else:
    export = ""
 
flag_cmd = ["--%s %s"%(a, "" if isinstance(b, bool) else b) for a,b in jdict.iteritems()] or [""]

def flagms(ms):
    utils.xrun("flag-ms.py", flag_cmd+[export, ms])


utils.pper(msname, flagms, ncpu)
