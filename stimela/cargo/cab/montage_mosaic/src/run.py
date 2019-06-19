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
    elif name == 'target_images':
        target_images = "--target_images " + " --target_images ".join(value)
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

if target_images:
    utils.xrun(cab['binary'], args+[target_images])
else:
    raise RuntimeError('Filenames of the images to be mosaicked have not been specified.')
