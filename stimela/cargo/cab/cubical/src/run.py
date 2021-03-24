# -*- coding: future_fstrings -*-
import os
import sys
import shlex
import configparser
import ast
from scabha import config, parameters_dict, prun
from casacore.tables import table
import re

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
    elif isinstance(value, list) and name not in ["model-list", "model-expr"]:
        value = ",".join(map(str, value))

    args[name] = value

# available jones terms
joneses = "g b dd".split()

dests = dict(msfile=os.environ["MSDIR"], output=os.environ["OUTPUT"], input=os.environ["INPUT"])
models = {}
tab = table(args['data-ms'])
cols = tab.colnames()
tab.close()
for i,model in enumerate(args['model-list']):
    if model.find(":") > 0:
        name, dest = model.split(":")
        dest = dests[dest]
        model = os.path.join(dest, name)
    elif model not in cols:
        model = os.path.join(dests['input'], model)
    models[i] = model
if not args.get('model-expr', None):
    args['model-list'] = ":".join(models.values())
else:
    model_list = []
    for expr in args['model-expr']:
        if expr.isdigit():
            model_list.append(models[int(expr)])
            continue
        match = re.match(r"(\d+)[\+-](\d+)", expr)
        if not hasattr(match, 'groups'):
            raise RuntimeError(f"The expression '{expr}' given to the cubical cab 'model-expr' option is not valid")
        first, last = match.groups()
        operand_idx = len(first)
        operand = expr[operand_idx]
        if operand == "-":
            operand = "+-"
        model_list.append( operand.join([ models[int(first)],models[int(last)] ])  )
    args['model-list'] = ":".join(model_list)
        
args.pop('model-expr', None)

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
if prun(argslist) is not 0:
    sys.exit(1)
