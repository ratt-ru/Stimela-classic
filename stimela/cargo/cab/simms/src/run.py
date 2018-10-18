import os
import sys

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

params = cab["parameters"]

_positional = ['antenna-file']
positional = []
for item in _positional:
    param = filter( lambda a: a['name']==item, params)[0]
    value = param['value']
    params.remove(param)

    if value:
        positional.append(value)

args = []
for param in params:
    key = param['name']
    value = param['value']
    if value in [None, False]:
        continue
    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], key)
    elif hasattr(value, '__iter__'):
        arg = ' '.join(['{0}{1} {2}'.format(cab['prefix'], key, val) for val in value])
    else:
        if isinstance(value, str):
            value = '"{}"'.format(value)
        arg = '{0}{1} {2}'.format(cab['prefix'], key, value)
    args.append(arg)

utils.xrun(cab['binary'], args+['--nolog']+positional)
