import os
import sys
import subprocess
import shlex
import glob
import shutil
import yaml


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

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

if not target_images:
    raise RuntimeError('Filenames of the images to be mosaicked have not been specified.')
_runc = " ".join([cab["binary"]] + args)

try:
    subprocess.check_call(shlex.split(_runc))
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
