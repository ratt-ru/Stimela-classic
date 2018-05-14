import os
import sys

sys.path.append("/scratch/stimela")
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTDIR = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = []
for param in cab['parameters']:
    value = param['value']
    name = param['name']

    if value in [None, False]:
        continue
    elif value is True:
        value = ""
    elif name == 'hdf5files':
        files = value
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

utils.xrun("h5toms.py", args+files )
