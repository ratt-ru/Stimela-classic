import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]

jdict = utils.readJson(CONFIG)
msname = "%s/%s"%("/msdir", jdict["msname"])

strategy = jdict.get("strategy", None)
strategy = "-s %s/%s"%(INPUT, strategy) if strategy else ""


flag_cmd = jdict.get("command", "")

utils.xrun("aoflagger", [flag_cmd, strategy, msname])
