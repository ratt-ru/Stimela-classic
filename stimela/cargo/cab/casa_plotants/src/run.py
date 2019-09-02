import os
import sys
import logging
import drivecasa
import logging
casa = drivecasa.Casapy(log2term=True, echo_to_stdout=True, timeout=24*3600*10)

sys.path.append("/scratch/stimela")

utils = __import__('utils')

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
    if result[1]:
        err = '\n'.join(result[1] if result[1] else [''])
        failed = err.lower().find('an error occurred running task') >= 0
        if failed:
            raise RuntimeError('CASA Task failed. See error message above')
        sys.stdout.write('WARNING:: SEVERE messages from CASA run')


result = casa.run_script(script, raise_on_severe=False)
log2term(result)
