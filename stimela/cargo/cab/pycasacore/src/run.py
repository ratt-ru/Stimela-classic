import os
import sys
import tempfile

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

with tempfile.NamedTemporaryFile(suffix=".py") as tfile:
    tfile.write(custom_script)
    tfile.flush()
    utils.xrun(cab['binary'], [tfile.name])
