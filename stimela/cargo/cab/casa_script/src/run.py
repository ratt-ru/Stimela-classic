import os
import sys
import yaml
import shlex
import shutil
import subprocess
import glob


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
    if value is None:
        continue
    elif value is False:
        continue
    elif value is True:
        value = ''
    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

with open("casajob.py.last", "w") as f:
    f.write(custom_script)


_runc = " ".join([cab['binary']] + ["-c", "casajob.py.last"] + args)
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
