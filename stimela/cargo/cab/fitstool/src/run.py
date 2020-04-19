import os
import sys
import shutil
import shlex
import subprocess
import shutil
import glob
import yaml

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

args = []
inimage = None
outimage = None
stack = False
unstack = False
axis = None
chunk = 1
file_pattern = False

for param in cab['parameters']:
    value = param['value']
    name = param['name']

    if value in [None, False]:
        continue

    if name == 'image':
        inimage = ' '.join(value)
        continue
    elif name == 'output':
        outimage = value
        continue
    elif name == 'stack':
        stack = True
        continue
    elif name == 'unstack':
        unstack = True
        continue
    elif name == 'unstack-chunk':
        chunk = value
        continue
    elif name == 'fits-axis':
        axis = value
        continue
    elif name == 'file_pattern':
        value = '"%s"' % value
        file_pattern = True

    elif value is True:
        value = ""

    args.append('{0}{1} {2}'.format(cab['prefix'], name, value))

if stack and axis:
    args.append('{0}stack {1}:{2}'.format(cab['prefix'], outimage, axis))
    outimage = None
elif unstack and axis:
    args.append('{0}unstack {1}:{2}:{3}'.format(
        cab['prefix'], outimage, axis, chunk))
    outimage = None
else:
    outimage = '{0}output {1}'.format(cab['prefix'], outimage)

if file_pattern:
    inimage = ""

_runc = " ".join([cab['binary']] + args + [inimage, outimage or ""])

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
