import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]

jdict = utils.readJson(CONFIG)

msnames = jdict["msname"]

if isinstance(msnames, (str, unicode)):
    msnames = [msnames]

msname = [ "%s/%s"%(os.environ["MSDIR"], ms) for ms in msnames ]


flag_cmd = jdict.pop("command", "")

def flagms(ms):
    utils.xrun("flag-ms.py", [flag_cmd, ms])

ncpu = jdict.get("ncpu", 1)

utils.pper(msname, flagms, ncpu)
