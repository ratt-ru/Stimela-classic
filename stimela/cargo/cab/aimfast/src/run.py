import os
import sys
import shlex
import shutil
import subprocess
import yaml
import glob


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]
args = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if value is None:
        continue

    if name in ['compare-images', 'compare-residuals', 'compare-models']:
        compare = []
        for i, val in enumerate(value):
            compare.append(val)
            # Compare models/images in pairs
            if i%2:
                args += ['{0}{1} {2}'.format(cab['prefix'],
                                             name, " ".join(compare))]
                compare = []
    elif name in ['compare-online', 'compare-residual-subimages', 'centre-pixels-size']:
        args += ['{0}{1} {2}'.format(cab['prefix'],
                                     name, " ".join(value))]
    elif param['dtype'] in ['bool']:
        args += ['{0}{1}'.format(cab['prefix'], name)]
    else:
        args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

_runc = " ".join([cab["binary"]]+ args)

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
