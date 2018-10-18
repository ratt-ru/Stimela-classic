import os
import sys

sys.path.append('/scratch/stimela')
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = []
parset = []

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
       parset = [value]
       continue
    elif name == 'model-list':
        if isinstance(value, str):
            value = [value]
        for i,val in enumerate(value):
            if not os.path.exists(val.split("@")[0]):
                value[i] = os.path.basename(val)
        value = ':'.join(value)
    elif isinstance(value, list):
        value = ",".join( map(str, value) )

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

utils.xrun(cab['binary'], parset+args)
