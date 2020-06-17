# -*- coding: future_fstrings -*-
import sys 
from scabha import config, parameters_dict, prun

args = []
for name, value in parameters_dict.items():
    if name == 'msname':
        if isinstance(value, str):
            mslist = value
        else:
            mslist = ' '.join(value)
        continue

    if value in [None, False]:
        continue
    elif name == "datacolumn":
        name = "data-column"

    elif name == 'scale':
        if isinstance(value, (int, float)):
            value = '{0}asec'.format(value)

    elif name in 'size trim nwlayers-for-size beam-shape channel-range interval'.split():
        if isinstance(value, (int, float)):
            value = [value]*2
        elif isinstance(value, list):
            if len(value) == 1:
                value = value*2

    if value is True:
        arg = [f'{config.prefix}{name}']
    else:
        if isinstance(value, list):
            value = list(map(str, value))
        elif isinstance(value, str):
            value = value.split()
        elif not isinstance(value, str):
            value = [str(value)]
        else:
            value = [value]
        arg = [f'{config.prefix}{name}' ] + value

    args += arg

args = [config.binary] + args + [mslist]

if prun(args) is not 0:
    sys.exit(1)
