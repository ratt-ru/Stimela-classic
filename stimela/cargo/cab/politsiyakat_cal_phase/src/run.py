import sys
import os
import json

sys.path.append("/scratch/stimela")
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

    args[name] = value

kwargs = "'{}'".format(json.dumps(args))

ARGS = ["flag_phase_drifts",
        "-s antenna_mod",
        kwargs]

utils.xrun(cab['binary'], ARGS)
