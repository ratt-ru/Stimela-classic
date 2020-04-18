import os
import sys
import yaml
import subprocess
import shlex
import glob
import shutil

CONFIG = os.environ["CONFIG"]
OUTPUT = os.environ["OUTPUT"]
INDIR = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

params = cab["parameters"]
junk = cab["junk"]

_positional = ['antenna-file']
positional = []
for item in _positional:
    param = filter(lambda a: a['name'] == item, params)[0]
    value = param['value']
    params.remove(param)

    if value:
        positional.append(value)

args = []
for param in params:
    key = param['name']
    value = param['value']
    if value in [None, False]:
        continue
    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], key)
    elif hasattr(value, '__iter__'):
        arg = ' '.join(['{0}{1} {2}'.format(cab['prefix'], key, val)
                        for val in value])
    else:
        if key in ["pol", "feed"]:
            value = '"{}"'.format(value)
        arg = '{0}{1} {2}'.format(cab['prefix'], key, value)
    args.append(arg)

_runc = " ".join([cab['binary']] + args + ['--nolog'] + positional)

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
