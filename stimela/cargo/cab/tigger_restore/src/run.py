import os
import sys
import subprocess
import glob
import yaml
import shlex
import shutil

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
        inim = value
        continue

    elif name == 'input-skymodel':
        inlsm = value
        continue

    elif name == 'output-image':
        outim = value
        continue

    args.append('{0}{1} {2}'.format(cab['prefix'], name, value))


_runc = " ".join([cab['binary']] + args + [inim, inlsm, outim])

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
