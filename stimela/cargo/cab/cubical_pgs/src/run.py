# -*- coding: future_fstrings -*-
import sys
from scabha import config, parameters_dict, prun, parse_parameters

args = [config.binary] + parse_parameters(parameters_dict)
# run the command
if prun(args) is not 0:
    sys.exit(1)


