import inner_taper as taper
import os
import sys

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
params = {}

msname = None
res = None
freq = None
reset = False
savefig = None

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if name == 'min-max-resolution':
        res = value
    elif name == 'frequency':
        freq = value
    elif name == 'reset':
        reset = value
    elif name == 'msname':
        msname = value
    elif name == 'save-figure':
        savefig = value
        

if reset:
    taper.reset(msname)
    sys.exit(0)

taper.taper(msname, res=res, freq=freq, savefig=savefig)

