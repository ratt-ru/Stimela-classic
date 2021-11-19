import os
import sys
import Tigger
import numpy
import tempfile
import json
import codecs
import shlex
import shutil
import glob
import subprocess

from astLib.astWCS import WCS
from Tigger.Models import SkyModel, ModelClasses


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with codecs.open(CONFIG, "r", "utf8") as stdr:
    cab = json.load(stdr)

junk = cab["junk"]
args = []
msname = None

sofia_file = 'sofia_parameters.par'
wstd = open(sofia_file, 'w')

wstd.write('writeCat.outputDir={:s}\n'.format(OUTPUT))
port2tigger = False
image = None
writecat = False
parameterise = False

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    if name == "port2tigger":
        port2tigger = value
        continue
    if name == "steps.doWriteCat":
        writecat = value
    if name == "steps.doParameterise":
        parameterise = value
    if name == "import.inFile":
        image = value

    wstd.write('{0}={1}\n'.format(name, value))

wstd.close()

_runc = " ".join(['sofia_pipeline.py', sofia_file])

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
