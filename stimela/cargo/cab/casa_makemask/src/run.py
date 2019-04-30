import os
import sys
import logging
import Crasa.Crasa as crasa

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

makemask_args = {}
immath_args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    if name in ['threshold', 'inpimage', 'outfile']:
        if name in ['threshold']:
            value = ' iif( IM0 >={:f}, IM0, 0.0) '.format(value)
            name = 'expr'
        if name in ['outfile']:
            value = '%s_thresh'.format(name)
        immath_args[name] = value

    if name in ['mode', 'inpimage', 'inpmask', 'output', 'overwrite']:
    	makemask_args[name] = value

task = crasa.CasaTask("immath", **immath_args)
task.run()

if 'inpmask' not in makemask_args:
    makemask_args['inputmask'] = immath_args['outfile']

task = crasa.CasaTask(cab["binary"], **makemask_args)
task.run()
