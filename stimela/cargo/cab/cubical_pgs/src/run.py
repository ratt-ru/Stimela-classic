# -*- coding: future_fstrings -*-
import sys
from scabha import config, parameters_dict, prun, parse_parameters

"""
config: 
    contains the sections before parameters in params.json
    .binary has the name of the binary to be executed
parameters_dict: dict
    contains all the provided parameters, even the positional ones
parse_parameters: function
    Forms a list containing all the provided arguments for execution.
    This is a helper function that formats stuff so that you don't have to
prun: function
    Execute your binary with the provided arguments
"""

args = [config.binary] + parse_parameters(parameters_dict)
# run the command

if prun(args) != 0:
    sys.exit(1)


