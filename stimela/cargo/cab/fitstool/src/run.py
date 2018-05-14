import os
import sys

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = []
inimage = None
outimage = None
stack = False
unstack = False
axis = None
chunk = 1

for param in cab['parameters']:
    value = param['value']
    name = param['name']

    if value in [None, False]:
        continue
    
    if name == 'image':
        inimage = ' '.join(value)
        continue
    elif name == 'output':
        outimage = value
        continue
    elif name == 'stack':
        stack = True
        continue
    elif name == 'unstack':
        unstack = True
        continue
    elif name == 'unstack-chunk':
        chunk = value
        continue
    elif name == 'fits-axis':
        axis = value
        continue

    elif value is True:
        value = ""

    args.append( '{0}{1} {2}'.format(cab['prefix'], name, value) )

if stack and axis:
    args.append( '{0}stack {1}:{2}'.format(cab['prefix'], outimage, axis))
    outimage = None
elif unstack and axis:
    args.append( '{0}unstack {1}:{2}:{3}'.format(cab['prefix'], outimage, axis, chunk))
    outimage = None
else:
    outimage = '{0}output {1}'.format(cab['prefix'], outimage)
utils.xrun(cab['binary'], args+[inimage, outimage or ""])
