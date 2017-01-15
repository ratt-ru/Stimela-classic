import os
import sys

sys.path.append('/utils')
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

    if value in [False, None]:
        continue

    if name == 'pa-range' and hasattr(value, '__iter__'):
        value = ','.join(value)
    if value is True:
        value = ""
    
    # Positional arguments
    if name == 'input-skymodel':
        inlsm = value
        continue
    elif name == 'output-skymodel':
        outlsm = value
        continue

    args.append( '{0}{1} {2}'.format(cab['prefix'], name, value) )

utils.xrun(cab['binary'], args+[inlsm, outlsm])
