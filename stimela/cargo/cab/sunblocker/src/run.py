import sys
import os
from sunblocker.sunblocker import Sunblocker
import inspect

sys.path.append("/scratch/stimela")
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

    if name == "command":
        function = value
        continue
    if value is None:
        continue

    args[name] = value

args['showdir'] = OUTPUT
run_func = getattr(Sunblocker(), function, None)
if run_func is None:
    raise RuntimeError("Function '{}' is not part of Sunblocker()".format(function))

## Reove default parameters that are not part of this particular function
sys.stdout.write(repr(args))
func_args = inspect.getargspec(run_func)[0]
for arg in args.keys():
    if arg not in func_args:
        args.pop(arg, None)

run_func(**args)
