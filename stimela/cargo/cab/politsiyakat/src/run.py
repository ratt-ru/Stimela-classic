import sys
import os
import json

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
tasksuite = None
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    elif name == "task":
        task = value
        continue
    elif name=='tasksuite':
        tasksuite = tasksuite

    args[name] = value

kwargs = "'{}'".format(json.dumps(args))

ARGS = [task, 
    ("-s " + tasksuite) if tasksuite is not None else (""), 
        kwargs]

utils.xrun(cab['binary'], ARGS)
