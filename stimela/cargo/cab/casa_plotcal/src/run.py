import os
import sys
import drivecasa
casa = drivecasa.Casapy()

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

args['showgui'] = False

script = ['{0}(**{1})'.format(cab['binary'], args)]

out, err = casa.run_script(script, raise_on_severe=False)
sys.stdout.write('\n'.join(out))

if len(err)>0:
        raise RuntimeError("Caught severe exception while running CASA task {0}. The error message is bellow \n {1}".format(cab['binary'], '\n'.join(err)))

