# -*- coding: future_fstrings -*-
import os
import sys
import shlex
import configparser
import ast
from scabha import config, parameters_dict, prun

args = {}
parset = []

for name, value in parameters_dict.items():
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

try:
    soljones = args.pop("sol-jones")
except KeyError:
    conf = configparser.SafeConfigParser(inline_comment_prefixes="#")
    conf.read(parset[0])
    if 'jones' in conf.options('sol'):
        soljones = conf.get('sol', 'jones')
        if "[" in soljones:
            soljones = ast.literal_eval(soljones)
        else:
            soljones = soljones.split(",")
    else:
        soljones = ['g', 'de']
    if type(soljones) is list:
        soljones = ",".join(soljones)

for jones in joneses:
    if jones.lower() not in soljones.lower():
        jopts = filter(lambda a: a.startswith(
            "{0:s}-".format(jones)), args.keys())
        for item in list(jopts):
            del args[item]

opts = ["{0:s}sol-jones {1:s}".format(config.prefix, soljones)] + \
    ['{0}{1} {2}'.format(config.prefix, name, value)
     for name, value in args.items()]

_runc = " ".join([config.binary] + parset + opts)

argslist = shlex.split(_runc)

# run the command
if prun(argslist) != 0:
    sys.exit(1)
