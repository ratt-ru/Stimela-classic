import os
import sys
import yaml

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = []
msname = None

rfinder_file = 'rfinder_default.yml'

with open(rfinder_file) as f:
    list_doc = yaml.load(f)

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    for par in list_doc:
        if par['name'] == name:
            par["value"] = value

with open(rfinder_file, "w") as f:
    yaml.dump(list_doc, f)

utils.xrun('rfinder', [rfinder_file])
