import os
import shlex
import shutil
import subprocess
import glob
from collections import OrderedDict
import json

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, 'rb') as stdr:
    cab = json.load(stdr, object_pairs_hook=OrderedDict)

junk = cab["junk"]
args = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    dtype = param["dtype"]
    if value is None:
        continue
    
    if name == "infits":
        infits = value
        continue
    
    if isinstance(value, list):
        values = map(str, value)
        args += [f"{cab['prefix']}{name} " + ",".join(values)]
    elif name == "output-prefix":
        args += [f"{cab['prefix']}{name} {OUTPUT}/{value}"]
    elif isinstance(dtype, str) and dtype == "bool":
        args += [f"{cab['prefix']}{name}"] 
    else:
        args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

binary = f"{os.environ['STIMELA_VENV_BIN']}/{cab['binary']}"
_runc = " ".join([binary] + args + [infits])


subprocess.check_call(shlex.split(f"echo '{_runc}'"))
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
