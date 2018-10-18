import os
import sys

sys.path.append('/scratch/stimela')
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

    if name in 'restoring-beam scale'.split() and hasattr(value, '__iter__'):
        value = ','.join(value)

    if value is True:
        value = ""
        if name == 'f':
            args.append('-f')
            continue

    # Positional arguments
    if name == 'input-image':
        inim= value
        continue

    elif name == 'input-skymodel':
        inlsm = value
        continue

    elif name == 'output-image':
        outim = value
        continue

    args.append( '{0}{1} {2}'.format(cab['prefix'], name, value) )

utils.xrun(cab['binary'], args+[inim, inlsm, outim])
