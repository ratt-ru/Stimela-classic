import os
import sys

sys.path.append('/scratch/stimela')
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if value is None:
        continue
    elif value is False:
        continue

    if type(value) is list:
        args += ['{0}{1} {2}'.format(cab['prefix'], name,
                 " ".join([val.replace(':output', '') for val in value]))]
    else:
        args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

utils.xrun(cab['binary'], args)
