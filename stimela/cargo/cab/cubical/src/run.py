import os
import sys

sys.path.append('/scratch/stimela')

utils = __import__('utils')

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
args = {}
parset = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    elif value is False:
        value = 0
    elif value is True:
        value = 1
    elif name == 'parset':
        parset = [value]
        continue
    elif isinstance(value, list):
        value = ",".join(map(str, value))

    args[name] = value

# available jones terms
joneses = "g b dd".split()
soljones = args.pop("sol-jones")

for jones in joneses:
    if jones.lower() not in soljones.lower():
        jopts = filter(lambda a: a.startswith(
            "{0:s}-".format(jones)), args.keys())
        for item in jopts:
            del args[item]

opts = ["{0:s}sol-jones {1:s}".format(cab["prefix"], soljones)] + \
    ['{0}{1} {2}'.format(cab['prefix'], name, value)
     for name, value in args.items()]

utils.xrun(cab['binary'], parset+opts)
