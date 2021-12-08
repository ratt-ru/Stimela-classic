#config -*- coding: future_fstrings -*-
import sys

from scabha import config, parse_parameters, prun

args = [config.binary] + parse_parameters(repeat=" ")
for i in range(len(args)):
    if args[i] == '--verb':
        val = args.pop(i+1)
        if val == 'False':
            args.pop(i)
        
# run the command
if prun(args) != 0:
    sys.exit(1)

