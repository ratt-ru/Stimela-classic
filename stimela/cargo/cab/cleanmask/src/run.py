import os
import sys
import shlex
import shutil
import yaml
import glob
import subprocess

OUTPUT = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

params = cab["parameters"]

args = []
for param in params:
    if param['value'] in [False, None]:
        continue
    elif param['value'] is True:
        arg = "{0}{1}".format(cab["prefix"], param["name"])
    else:
        arg = "{0}{1} {2}".format(cab["prefix"], param["name"], param["value"])

    args.append(arg)

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

