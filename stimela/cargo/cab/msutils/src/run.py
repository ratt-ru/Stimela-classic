import sys
import os
from MSUtils import msutils
import MSUtils.ClassESW as esw
import inspect
from MSUtils.imp_plotter import gain_plotter

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

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
    if isinstance(args['stats_data'], str) and args['stats_data'].find('use_package_meerkat_spec')>=0:
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
   gain_plotter(tab,tabtype,outfile,scale,dpi)
   sys.exit(0)
   
   
run_func = getattr(msutils, function, None)
if run_func is None:
    raise RuntimeError("Function '{}' is not part of MSUtils".format(function))

## Reove default parameters that are not part of this particular function
func_args = inspect.getargspec(run_func)[0]
for arg in args.keys():
    if arg not in func_args:
        args.pop(arg, None)

run_func(**args)
