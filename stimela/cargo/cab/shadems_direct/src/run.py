import os
import sys
import shlex
import yaml
import subprocess
import shutil
import glob
import traceback

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]
args = []
params = {param['name']:param['value'] for param in cab['parameters']}

ms = params['ms']
args_list = params['args']

errors = []

for args in args_list:
    _runc = " ".join([cab["binary"], ms, args])
    print("Running", _runc)
    try:
        subprocess.check_call(shlex.split(_runc))
    except subprocess.CalledProcessError as exc:
        errors.append((_runc, exc))

for item in junk:
    for dest in [OUTPUT, MSDIR]:  # these are the only writable volumes in the container
        items = glob.glob("{dest}/{item}".format(**locals()))
        for f in items:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)
            # Leave other types

for cmd, exc in errors:
    print(f"ERROR: {cmd}: failed with return code {exc.returncode}")

if errors and not params.get('ignore_errors'):
    sys.exit(1)

