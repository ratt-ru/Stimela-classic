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

rfinder_file = '/build/rfinder/rfinder_default.yml'

with open(rfinder_file) as f:
    list_doc = yaml.load(f)


list_doci['general']['outdir'] = OUTPUT
list_doci['general']['workdir'] = MSDIR


for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    for par in list_doc.keys():
	if type(par) == dict:
            for p in par.keys():
                if pa == name:
                    list_doc[par][p] = value
	else:
            if par == name:
                list_doc[par] = value

with open(rfinder_file, "w") as f:
    yaml.dump(list_doc, f)

utils.xrun('rfinder', [rfinder_file])
