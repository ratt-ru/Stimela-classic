import os
import sys
import shlex
import shutil
import subprocess
import yaml
import glob

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

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
        if isinstance(value, str):
            msname = value
        else:
            msname = ' '.join(value)
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

if msname is None:
    raise RuntimeError('MS name has not be specified')

_runc = " ".join([cab['binary']] + args + [msname])
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
