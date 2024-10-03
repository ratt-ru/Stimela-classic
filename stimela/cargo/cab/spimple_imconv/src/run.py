# -*- coding: future_fstrings -*-
import sys

from scabha import config, parse_parameters, prun

pars = parse_parameters(repeat=" ")
if "--psf-pars" in pars:
    pars = " ".join(pars).split()

args = [config.binary] + pars
    
# run the command
if prun(args) != 0:
    sys.exit(1)

