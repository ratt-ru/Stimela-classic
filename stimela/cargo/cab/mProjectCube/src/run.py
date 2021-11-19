# -*- coding: future_fstrings -*-
import sys

from scabha import config, parse_parameters, prun

# If a list of fields is given, insert them as repeated arguments.
# Other arguments not allowed to be lists.
args = [config.binary] + parse_parameters(repeat=True)

# run the command
if prun(args) != 0:
    raise SystemError(f" {config.binary} exited with a non-zero code. See logs for details")
