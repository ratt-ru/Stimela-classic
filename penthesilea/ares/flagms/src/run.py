import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]

jdict = utils.readJson(CONFIG)
msname = "%s/%s"%(os.environ["MSDIR"], utils.pop["msname"])


flag_cmd = jdict.pop("command")

utils.xrun("flag-ms.py", [flag_cmd, msname])
