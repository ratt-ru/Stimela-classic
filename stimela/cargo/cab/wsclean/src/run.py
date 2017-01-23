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
        mslist = ' '.join(value)
        continue

    if value in [None, False]:
        continue
    # only versions > 2.0 have this 
    if name in ["spws"]:
        continue

    if name == 'scale':
        if isinstance(value, (int, float)):
            value = '{0}asec'.format(value)

    if name in 'size trim nwlayers-for-size beamshape'.split():
        if isinstance(value, int):
            value = '{0} {0}'.format(value)
        elif getattr(value, '__iter__'):
            if len(value) == 1:
                value.append( value[0])
            value = ' '.join(map(str, value))

    if name in 'spws multiscale-scales pol'.split():
        if getattr(value, '__iter__'):
            value = ','.join(map(str, value))

    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], name)
    else:
        arg = '{0}{1} {2}'.format(cab['prefix'], name, value)

    args.append(arg)

utils.xrun(cab['binary'], args + [mslist])
