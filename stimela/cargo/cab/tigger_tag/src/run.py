import os
import sys

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
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
        inlsm= value
        continue
    elif name == 'tag':
        tag = value
        continue

    params[name] = value

#TODO: Need fix tigger-tag, these kludges are annoying
if params.pop('transfer-tags', False) in [True, ""]:
    if params.get('tolerance', None) is None:
        raise RuntimeError("Parameter 'tolerance' is required when 'transfer-tags' is enables")
    args = ['{0}transfer-tags {1}:{2}'.format(cab['prefix'], inlsm, params.pop('tolerance'))]
    inlsm = params.get('output')
else:
    args = []

args += ['{0}{1} {2}'.format(cab['prefix'], name, value) for name, value in params.iteritems()]
utils.xrun(cab['binary'], args+[inlsm, tag])
