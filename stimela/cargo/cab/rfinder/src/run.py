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


list_doc['general']['outdir'] = '{:s}/'.format(OUTPUT)
list_doc['general']['workdir'] = '{:s}/'.format(MSDIR)

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    msnames = []
    if name == 'msname':
        for ms in value:
            msnames.append(ms.split('/')[-1])
        list_doc['general']['msname'] = msnames
        continue

    for key, val in list_doc.items():
        if type(val) == dict:
            for k1, v1 in val.items():
                if type(v1) == dict:
                    for k2, v2 in v1.items():
                        if k2 == name:
                            list_doc[key][k1][k2] = value
                else:
                    if k1 == name:
                        list_doc[key][k1] = value
        else:
            if key == name:
                list_doc[key] = value

edited_file = 'rfinder_default.yml'
with open(edited_file, "w") as f:
    yaml.dump(list_doc, f)

utils.xrun('rfinder', [edited_file])
