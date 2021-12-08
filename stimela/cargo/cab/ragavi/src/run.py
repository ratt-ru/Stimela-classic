# -*- coding: future_fstrings -*-
import sys

from scabha import config, parse_parameters, prun

args = [config.binary] + parse_parameters(repeat=" ")

# run the command
if prun(args) != 0:
    sys.exit(1)

