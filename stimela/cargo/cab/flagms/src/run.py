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

    if value in [False, None]:
        continue

    if name in 'channels timeslots corrs stations ddid field str'.split():
        if name in 'channels timeslots'.split():
            value = ':'.join(value)
        else:
            value = ','.join(value)
    if value is True:
        value = ""

    if name == 'msname':
        msname = value
        if isinstance(msname, str):
            msname = [msname]
        continue

    if name == 'flagged-any':
        args += ['{0}flagged-any {1}'.format(cab['prefix'], a) for a in value]
        continue

    args.append('{0}{1} {2}'.format(cab['prefix'], name, value))

_runc = " ".join([cab["binary"]] + args + msname)

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
