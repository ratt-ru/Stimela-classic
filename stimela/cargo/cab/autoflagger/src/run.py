import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)
msname = jdict.pop("msname")

if isinstance(msname, (str, unicode)):
    msname = [msname]

msname = " ".join( ["%s/%s"%(MSDIR , ms)  for ms in msname] )

strategy = jdict.pop("strategy", None)
if strategy:
    strategy = utils.substitute_globals(strategy) or INPUT + "/" + strategy
strategy = "-strategy %s"%(strategy) if strategy else ""

flag_cmd = ["-%s %s"%(a, "" if isinstance(b, bool) else b) for a,b in jdict.iteritems()] or [""]
utils.xrun("aoflagger", flag_cmd+[strategy, msname])
