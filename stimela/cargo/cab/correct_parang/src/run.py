import glob
import os
import shutil
import subprocess
import sys
import yaml

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]
args = []
msname = None
script = os.path.join(os.path.dirname(__file__), "correct_parang.py")

for param in cab["parameters"]:
    name = param["name"]
    value = param["value"]

    if value is None:
        continue
    if name == "msname":
        msname = value
        continue
    if value is False:
        continue
    if value is True:
        args.append("{0}{1}".format(cab["prefix"], name))
    else:
        args.extend(["{0}{1}".format(cab["prefix"], name), "{0}".format(value)])

cmd = [sys.executable, script]
if msname is not None:
    cmd.append(msname)
cmd.extend(args)

try:
    subprocess.check_call(cmd)
finally:
    for item in junk:
        for dest in [
            OUTPUT,
            MSDIR,
        ]:
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
