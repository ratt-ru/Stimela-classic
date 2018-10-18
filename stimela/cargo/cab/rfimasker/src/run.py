import os
import sys

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = []
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if name == 'ms':
        mslist = ' '.join(value)
        continue
    if value in [None, False]:
       continue
    if value is True:
        value = ""
    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

utils.xrun("mask_ms.py", args + [mslist])
