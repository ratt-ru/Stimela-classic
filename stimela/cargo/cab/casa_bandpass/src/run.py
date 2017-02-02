import os
import sys
import drivecasa
casa = drivecasa.Casapy(log2term=True, echo_to_stdout=True, timeout=24*3600) 
# I set timeout to a day. Not my business to
# decide how long the process should tak

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value

script = ['{0}(**{1})'.format(cab['binary'], args)]

_, err = casa.run_script(script, raise_on_severe=False)

if len(err)>0:
    raise RuntimeError("Caught severe exception while running CASA task {0}. The error message is above".format(cab['binary']))
