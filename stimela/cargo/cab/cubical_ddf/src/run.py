import os
import sys
import shlex
import shutil
import subprocess
import glob
import yaml

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

args = {}
parset = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    elif value is False:
        value = 0
    elif value is True:
        value = 1
    elif name == 'parset':
        parset = [value]
        continue
    elif isinstance(value, list):
        value = ",".join(map(str, value))

    args[name] = value

# available jones terms
joneses = "g b dd".split()
soljones = args.pop("sol-jones")

for jones in joneses:
    if jones.lower() not in soljones.lower():
        jopts = filter(lambda a: a.startswith(
            "{0:s}-".format(jones)), args.keys())
        for item in list(jopts):
            del args[item]

opts = ["{0:s}sol-jones {1:s}".format(cab["prefix"], soljones)] + \
    ['{0}{1} {2}'.format(cab['prefix'], name, value)
     for name, value in args.items()]

_runc = " ".join([cab["binary"]] + parset + opts)
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
