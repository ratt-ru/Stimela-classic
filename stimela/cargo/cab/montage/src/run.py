import os
import sys

sys.path.append('/utils')
import utils
import montage_wrapper as montage


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    if name == "output_dir":
        args["output_dir"] = os.path.join(OUTPUT, value)

    args[name] = value

montage.mosaic(**args)
