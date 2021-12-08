import os
import sys
import glob
import subprocess
import yaml
import shutil
import shlex

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

params = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value in [False, None]:
        continue

    if value is True:
        value = ""

    # Positional arguments
    if name == 'input-skymodel':
        inlsm = value
        continue
    elif name == 'tag':
        tag = value
        continue

    params[name] = value

# TODO: Need fix tigger-tag, these kludges are annoying
if params.pop('transfer-tags', False) in [True, ""]:
    if params.get('tolerance', None) is None:
        raise RuntimeError(
            "Parameter 'tolerance' is required when 'transfer-tags' is enables")
    args = [
        '{0}transfer-tags {1}:{2}'.format(cab['prefix'], inlsm, params.pop('tolerance'))]
    inlsm = params.get('output')
else:
    args = []

args += ['{0}{1} {2}'.format(cab['prefix'], name, value)
         for name, value in params.iteritems()]

_runc = " ".join([cab.binary, inlsm, tag] + args)

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
