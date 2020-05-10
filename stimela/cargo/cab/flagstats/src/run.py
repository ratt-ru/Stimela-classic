import sys
import os
from MSUtils import flag_stats
import inspect
import glob
import shutil
import yaml
import codecs
import json

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

    if name in ["fields", "antennas"] and value is not None:
        try:
            value = list(map(int, value))
        except ValueError:
            pass
    if name == "outfile":
        outfile = value
        continue
    args[name] = value

try:
    stats = flag_stats.antenna_flags_field(**args)
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)

with codecs.open(outfile, 'w', 'utf8') as stdw:
    a = json.dumps(stats, ensure_ascii=False)
    stdw.write(a)
