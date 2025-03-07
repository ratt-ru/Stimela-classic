import sys
import os

INDIR = os.environ["INPUT"]
OUTDIR = os.environ["OUTPUT"]

from scabha import config, parse_parameters, prun

pars = parse_parameters(repeat=" ")

args = [config.binary, "--input", INDIR + '/', "--output", OUTDIR + '/'] + pars
 
# run the command
if prun(args) != 0:
    sys.exit(1)
