import os
import sys
import yaml
import rfinder
import glob
import subprocess
import shlex
import shutil


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]
args = []
msname = None

pkg_path = os.path.dirname(os.path.realpath(rfinder.__file__))
rfinder_file = '{:s}/rfinder_default.yml'.format(pkg_path)

with open(rfinder_file) as f:
    list_doc = yaml.load(f)

list_doc['general']['outdir'] = '{:s}/'.format(OUTPUT)
list_doc['general']['workdir'] = '{:s}/'.format(MSDIR)

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    if name == 'msname':
        list_doc['general']['msname'] = value.split('/')[-1]
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


_runc = 'rfinder -c %s' % edited_file

try:
    subprocess.check_call(shlex.split(_runc))
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
                # Leave other types

