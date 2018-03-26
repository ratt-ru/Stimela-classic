import os
import sys

sys.path.append('/utils')
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = []
parset = '/code/DefaultParset.cfg'

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    elif value is False:
        value = 0
    elif value is True:
        value = 1
    elif name == 'parset':
       parset = value
       continue
    elif name == 'model-list':
        value = ':'.join(value)

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

utils.xrun(cab['binary'], [parset]+args)
