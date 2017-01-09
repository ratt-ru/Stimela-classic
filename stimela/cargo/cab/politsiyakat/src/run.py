import os
import sys

sys.path.append('/utils')
import utils
import json

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

# only msname, task and tasksuite is extracted, the rest must be handled
# in your Stimela script
msname = jdict.pop("msname")
taskname = jdict.pop("task")
try:
    tasksuite = jdict.pop("tasksuite")
except:
    tasksuite = None

assert isinstance(msname, (str, unicode)), "msname parameter must be string"
msname = "%s/%s"%(MSDIR, msname)

# after parsing push msname back into the dictionary
jdict["msname"] = msname
kwargs = "'%s'" % json.dumps(jdict)

EXEC = ["-m", "politsiyakat"]
ARGS = [taskname, 
	("-s " + tasksuite) if tasksuite is not None else (""), 
	kwargs]
utils.xrun("python", EXEC + ARGS)

