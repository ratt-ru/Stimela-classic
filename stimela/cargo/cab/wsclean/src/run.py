import os
import sys
import re
import yaml
import subprocess
import shlex
import glob

CONFIG = os.environ['CONFIG']
INPUT = os.environ['INPUT']
OUTPUT = os.environ['OUTPUT']
MSDIR = os.environ['MSDIR']

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

params = cab['parameters']
junk = cab["junk"]
args = []

for param in params:
    name = param['name']
    value = param['value']

    if name == 'msname':
        if isinstance(value, str):
            mslist = value
        else:
            mslist = ' '.join(value)
        continue

    if value in [None, False]:
        continue
    elif name == "datacolumn":
        name = "data-column"

    elif name == 'scale':
        if isinstance(value, (int, float)):
            value = '{0}asec'.format(value)

    elif name in 'size trim nwlayers-for-size beam-shape channel-range interval'.split():
        if isinstance(value, int):
            value = '{0} {0}'.format(value)
        elif hasattr(value, '__iter__'):
            if len(value) == 1:
                value.append(value[0])
            value = ' '.join(map(str, value))

    elif name in 'spws multiscale-scales pol'.split():
        if hasattr(value, '__iter__'):
            value = ','.join(map(str, value))

    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], name)
    else:
        arg = '{0}{1} {2}'.format(cab['prefix'], name, value)

    args.append(arg)

_runc = " ".join([cab["binary"]] + args + [mslist])

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
                # Leave other types
