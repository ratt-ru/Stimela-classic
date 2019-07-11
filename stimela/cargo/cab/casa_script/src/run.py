import os
import sys

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = []
msname = None

custom_script = "print(\"Nothing has been done\")"

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if name == "script":
        custom_script = value
        continue
    if value is None:
        continue
    elif value is False:
        continue
    elif value is True:
        value = ''
    args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]

with open("casajob.py.last", "w") as f:
    f.write(custom_script)
utils.xrun(cab['binary'], ["-c", "casajob.py.last"] + args)
