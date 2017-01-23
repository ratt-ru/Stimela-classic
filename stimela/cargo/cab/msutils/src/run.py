import sys
import os
from MSUtils import msutils
import inspect

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value in [None, False]:
        continue
    if value is True:
        value = ""
    if name == "command":
        function = value
        continue

    args[name] = value

run_func = getattr(msutils, function, None)
if run_func is None:
    raise RuntimeError("Function '{}' is not part of MSUtils".format(function))

## Reove default parameters that are not part of this particular function
func_args = inspect.getargspec(run_func)[0]
for arg in args.keys():
    if arg not in func_args:
        args.pop(arg, None)

run_func(**args)
