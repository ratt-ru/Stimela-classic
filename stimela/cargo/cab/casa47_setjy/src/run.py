import os
import sys
import drivecasa
import logging
import shlex
import shutil
import subprocess
import yaml
import glob
casa = drivecasa.Casapy(log2term=True, echo_to_stdout=True, timeout=24*3600*10)


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

try:
    result = casa.run_script(script, raise_on_severe=False)
    log2term(result)
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
