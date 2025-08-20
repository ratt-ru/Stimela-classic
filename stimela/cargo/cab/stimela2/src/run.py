#!/usr/bin/env python3
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

    if name in ['recipe']:
        recipe = value
        continue

    if name in ['recipe-name']:
        recipe_name = value
        continue

    if name in ['support-files']:
        continue

    if name in ['step']:
        delimiter = ',' #param['delimiter']
        args += ['{0}{1} {2}'.format(cab['prefix'], name, delimiter.join(value))]

    if name in  ['params']:
        delimiter = ' ' #param['delimiter']
        args += ['{0}'.format(delimiter.join(value))]

_runc = " ".join([cab["binary"]] + [recipe, recipe_name] + args)

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
