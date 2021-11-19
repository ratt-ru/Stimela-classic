# -*- coding: future_fstrings -*-
import sys

from scabha import config, parse_parameters, prun

# If a list of fields is given, insert them as repeated arguments.
# Other arguments not allowed to be lists.
args = [config.binary] + parse_parameters(repeat=True,
                                          positional=["dirty-pdf", "rmsf-fwhm"], mandatory=["dirty-pdf", "rmsf-fwhm"])

# run the command
if prun(args) !=0:
    sys.exit(1)
