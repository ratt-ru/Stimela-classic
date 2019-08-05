import os
import sys

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = []
targets = None
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    elif value is False:
        continue
    elif value is True:
        value = ''
    elif name == 'target-images':
        targets = value
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

indir = os.path.dirname(targets[0])
target_names = map(os.path.basename, targets)
target_images = "--target-images " + " --target-images ".join(target_names)

args += ["--input {0:s} {1:s} --output {2:s}".format(indir, target_images,
    OUTPUT)]

if target_images:
    utils.xrun(cab['binary'], args)
else:
    raise RuntimeError('Filenames of the images to be mosaicked have not been specified.')
