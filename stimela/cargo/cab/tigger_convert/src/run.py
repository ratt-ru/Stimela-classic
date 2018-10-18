import os
import sys

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
mslist = []
field = []

args = []
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value in [False, None]:
        continue
    if name == "primary-beam":
        value = "'{}'".format(value)
    if name == 'pa-range' and hasattr(value, '__iter__'):
        value = ','.join(value)
    if value is True:
        value = ""
    if name == 'pa-from-ms' and hasattr(value, '__iter__'):
        mslist = value
        continue
    if name == 'field-id'and hasattr(value, '__iter__'):
        field = value
        continue

    # Positional arguments
    if name == 'input-skymodel':
        inlsm = value
        continue
    elif name == 'output-skymodel':
        outlsm = value
        continue

    args.append( '{0}{1} {2}'.format(cab['prefix'], name, value) )

if mslist:
    if len(field)==0:
        field = [0]*len(mslist)
    pa_from_ms = ','.join(['{0}:{1}'.format(ms, i) for ms,i in zip(mslist, field)])
    args.append('--pa-from-ms {}'.format(pa_from_ms))

utils.xrun(cab['binary'], args + [inlsm, outlsm])
