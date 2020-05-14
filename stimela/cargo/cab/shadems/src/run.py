import os
import sys
import shlex
import yaml
import subprocess
import json
import shutil
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
    elif value is False:
        continue
    if name == "ms":
        ms = value
        continue
    elif name in ["debug", "iter-scan", "iter-field", "iter-corr", "iter-spw", "iter-antenna", "noconj", "noflags", "profile"]:
        value = ""

    if isinstance(value, list):
        val = map(str, value)
        args += ['{0}{1} {2}'.format(cab['prefix'], name, " ".join(val))]
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

_runc = " ".join([cab["binary"]] + args + ["--dir", OUTPUT]  + [ms])

try:
    subprocess.check_call(shlex.split(_runc))
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]:  # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
                # Leave other types
