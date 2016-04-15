import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)
msname = jdict["msname"]

if isinstance(msname, (str, unicode)):
    msname = [msname]

msname = " ".join( ["%s/%s"%(MSDIR , ms)  for ms in msname] )

strategy = jdict.get("strategy", None)
strategy = "-s %s/%s"%(INPUT, strategy) if strategy else ""


flag_cmd = jdict.get("command", "")

utils.xrun("aoflagger", [flag_cmd, strategy, msname])
