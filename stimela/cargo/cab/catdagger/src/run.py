import os
import sys
import shlex
import shutil
import subprocess
import glob
import yaml

OUTPUT = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

args = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if name == "noise-map":
        args += [value]
        continue
    if value is None:
        continue
    elif value is False:
        continue
    if param["dtype"] == "bool" and value:
        args += ['{0}{1}'.format(cab['prefix'], name)]
        continue
    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

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
