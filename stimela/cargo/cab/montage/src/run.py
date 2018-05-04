import os
import sys

sys.path.append('/utils')
import utils
import montage_wrapper as montage


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value
args["output_dir"] = OUTPUT

montage.mosaic(**args)
