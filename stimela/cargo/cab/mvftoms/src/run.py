import os
import sys
import glob
import subprocess
import shutil
import shlex
import yaml

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTDIR = os.environ["OUTPUT"]
HOME = os.environ["HOME"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

args = []
overwrite = False

for param in cab['parameters']:
    value = param['value']
    name = param['name']

    if value in [None, False]:
        continue
    elif name == "overwrite":
        overwrite = value
        continue
    elif value is True:
        value = ""
    elif name == 'mvffiles':
        files = value
        continue
    elif name == "output-ms" and value:
        ms = value
    elif name == "credentials_dir" and value:
        os.system("cp -rf {0:s} {1:s}/.aws".format(value, HOME))
        continue
    elif name == "archive-url":
        files = value
        continue

    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

if overwrite:
    os.system("rm -fr {0:s}".format(ms))

_runc = " ".join([cab["binary"]] + args + files)
try:
    subprocess.check_call(shlex.split(_runc))
finally:
    for item in junk:
        for dest in [OUTDIR, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
