import sys
import os
from sunblocker.sunblocker import Sunblocker
import inspect
import yaml
import subprocess
import glob
import shlex
import shutil

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if name == "command":
        function = value
        continue
    if value is None:
        continue

    args[name] = value

args['showdir'] = OUTPUT
run_func = getattr(Sunblocker(), function, None)
if run_func is None:
    raise RuntimeError(
        "Function '{}' is not part of Sunblocker()".format(function))

func_args = inspect.getargspec(run_func)[0]
for arg in args.keys():
    if arg not in func_args:
        args.pop(arg, None)

try:
    run_func(**args)
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
