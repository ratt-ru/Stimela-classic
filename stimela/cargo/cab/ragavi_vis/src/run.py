# -*- coding: future_fstrings -*-
import sys

from scabha import config, parameters, prun

args = [config.binary]

# convert arguments to flat list of PrefixName Arguments
for name, value in parameters.items():
    if value in [None, "", " ", False]:
        continue
    args.append(f'{config.prefix}{name}')

    if not isinstance(value, list):
        value = [value]

    args += list(map(str, value))

# run the command
if prun(args) != 0:
    sys.exit(1)

