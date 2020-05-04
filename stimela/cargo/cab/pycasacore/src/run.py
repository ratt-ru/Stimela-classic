import os
import sys
import tempfile
import shlex
import shutil
import yaml
import glob
import subprocess


CONFIG = os.environ["CONFIG"]
OUTPUT = os.environ["OUTPUT"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

args = []
msname = None

custom_script = "print(\"Nothing has been done\")"

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if name == "script":
        custom_script = value
        continue

with tempfile.NamedTemporaryFile(suffix=".py") as tfile:
    tfile.write(custom_script)
    tfile.flush()

    _runc = " ".join([cab["binary"], tfile.name])
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
