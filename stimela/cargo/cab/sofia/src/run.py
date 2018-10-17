import os
import sys

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = []
msname = None

sofia_file = 'sofia_parameters.par'
wstd = open(sofia_file, 'w')

wstd.write('writeCat.outputDir={:s}\n'.format(OUTPUT))

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    
    if value is None:
        continue
    print name, value
	
    wstd.write('{0}={1}\n'.format(name, value))

wstd.close()

utils.xrun('sofia_pipeline.py', [sofia_file])
