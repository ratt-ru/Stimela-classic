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

args = []
parset = None
for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if name == 'Parset' and value is not None:
        parset = value
        continue
    if name == 'Parset' and value is None:
        continue

    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], name)
    else:
        arg = '{0}{1} {2}'.format(cab['prefix'], name, value)

    args.append(arg)

if parset is not None:
    args.insert(0, parset)
utils.xrun(cab['binary'], args)
