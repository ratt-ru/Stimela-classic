import sys
import os
from MSUtils import msutils
import inspect

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value in [None, False]:
        continue
    if value is True:
        value = ""
    if name == "task":
        task = value
        continue

    args.append( '{0}{1} {2}'.format(cab['prefix'], name, value))

utils.xrun(cab['binary'], args)
