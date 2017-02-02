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

script = ['{0}(**{1})'.format(cab['binary'], args)]

def log2term(result):
    if result[0]:
        out = '\n'.join(result[0])
        sys.stdout.write(out)
    if result[1]:
        err = '\n'.join(result[1] if result[1] else [''])
        failed = err.lower().find('an error occurred running task')>=0
        if failed:
            raise RuntimeError('CASA Task failed. See error message bellow \n {}'.format(err))
        sys.stdout.write('WARNING:: SEVERE messages from CASA run: \n {}'.format(err))

result = casa.run_script(script, raise_on_severe=False)
log2term(result)

#out, err = casa.run_script(script, raise_on_severe=False)
#sys.stdout.write('\n'.join(out))

#if len(err)>0:
#    raise RuntimeError("Caught severe exception while running CASA task {0}. The error message is bellow \n {1}".format(cab['binary'],  '\n'.join(err)))










