import sys
import os
from MSUtils import msutils
import MSUtils.ClassESW as esw
import inspect
from MSUtils.imp_plotter import gain_plotter
import glob
import shutil
import yaml


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]
args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if name == "command":
        function = value
        continue

    args[name] = value

if function == 'sumcols':
    args['outcol'] = args.pop('colname')

if function == "estimate_weights":
    msnoise = esw.MSNoise(args['msname'])
    if isinstance(args['stats_data'], str) and args['stats_data'].find('use_package_meerkat_spec') >= 0:
        args['stats_data'] = esw.MEERKAT_SEFD

    # Calculate noise/weights from spec
    noise, weights = msnoise.estimate_weights(stats_data=args['stats_data'],
                                              smooth=args['smooth'],
                                              fit_order=args['fit_order'],
                                              plot_stats=args.get('plot_stats', None))

    if args['write_to_ms']:
        msnoise.write_toms(noise, columns=args['noise_columns'])
        msnoise.write_toms(weights, columns=args['weight_columns'])
    sys.exit(0)

if function == "plot_gains":
    tab = args['ctable']
    tabtype = args['tabtype']
    dpi = args['plot_dpi']
    scale = args['subplot_scale']
    outfile = args['plot_file']
    gain_plotter(tab, tabtype, outfile, scale, dpi)
    sys.exit(0)


run_func = getattr(msutils, function, None)
if run_func is None:
    raise RuntimeError("Function '{}' is not part of MSUtils".format(function))

# Filter default parameters that are part of this function
func_args = inspect.getargspec(run_func)[0]
_args = {}
for arg in args.keys():
    if arg in func_args:
        _args[arg] = args[arg]

try:
    run_func(**_args)
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
