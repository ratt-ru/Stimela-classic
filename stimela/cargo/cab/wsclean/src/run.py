import os
import sys
import re

sys.path.append('/utils')
import utils

CONFIG = os.environ['CONFIG']
INPUT = os.environ['INPUT']
OUTPUT = os.environ['OUTPUT']
MSDIR = os.environ['MSDIR']

cab = utils.readJson(CONFIG)
params = cab['parameters']
args = []

for param in params:
    name = param['name']
    value = param['value']

    if name == 'msname':
        mslist = value
        continue

    if value in [None, False]:
        continue
    
    if name in ["spws"]:
        continue

    if name == 'scale':
        if isinstance(value, (int, float)):
            value = '{0}asec'.format(value)
    if name in 'size trim nwlayers-for-size'.split():
        try:
            v = float(value)
            value = '{0} {0}'.format(value)
        except ValueError:
            pass

    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], name)
    else:
        arg = '{0}{1} {2}'.format(cab['prefix'], name, value)

    args.append(arg)

utils.xrun(cab['binary'], args + [mslist])
