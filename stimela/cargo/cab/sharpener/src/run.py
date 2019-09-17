import os
import sys
import yaml
import sharpener

sys.path.append('/scratch/stimela')

utils = __import__('utils')


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = []
msname = None

pkg_path = os.path.dirname(os.path.realpath(sharpener.__file__))
sharpener_file = '{:s}/sharpener_default.yml'.format(pkg_path)

with open(sharpener_file) as f:
    list_doc = yaml.load(f)

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    for key, val in list_doc.items():
        if type(val) == dict:
            for k1, v1 in val.items():
                if 'enable' in name:
                    if key in name:
                        list_doc[key]['enable'] = value
                elif k1 == name:
                    list_doc[key][k1] = value
        else:
            if key == name:
                list_doc[key] = value

# Get the relative path from workdir
list_doc['general']['contname'] = os.path.relpath(
        list_doc['general']['contname'], list_doc['general']['workdir'])
list_doc['general']['cubename'] = os.path.relpath(
        list_doc['general']['cubename'], list_doc['general']['workdir'])
list_doc['source_catalog']['catalog_file'] = os.path.relpath(
        list_doc['source_catalog']['catalog_file'], list_doc['general']['workdir'])

edited_file = 'sharpener_default.yml'
with open(edited_file, "w") as f:
    yaml.dump(list_doc, f)

utils.xrun('run_sharpener -c ', [edited_file])
