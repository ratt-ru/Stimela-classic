import os
import sys

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = []
msname = None
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    elif value is False:
        continue
    elif value is True:
        value = ''
    elif name == 'msname':
        msname = ' '.join(value)
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

if msname:
    utils.xrun(cab['binary'], args+[msname])
else:
    raise RuntimeError('MS name has not be specified')
