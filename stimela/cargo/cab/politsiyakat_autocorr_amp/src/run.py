import sys
import os
import json
import yaml
import subprocess
import shlex
import shutil
import glob

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

args = {}
tasksuite = None
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value

kwargs = "'{}'".format(json.dumps(args))

ARGS = ["flag_autocorr_drifts",
        "-s antenna_mod",
        kwargs]

_runc = " ".join([cab['binary']] + ARGS)
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
