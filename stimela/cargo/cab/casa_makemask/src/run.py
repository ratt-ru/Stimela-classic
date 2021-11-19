# -*- coding: future_fstrings -*-
import Crasa.Crasa as crasa
from scabha import config, parameters_dict, prun

print(f"Running CASA task '{config.binary}'")

makemask_args = {}
immath_args = {}
for name, value in parameters_dict.items():
    if value is None:
        continue

    if name in ['threshold', 'inpimage', 'output']:
        if name in ['threshold']:
            im_value = ' iif( IM0 >=%s, IM0, 0.0) ' % value
            im_name = 'expr'
        if name in ['output']:
            im_value = '%s_thresh' % value
            im_name = 'outfile'
        if name in ['inpimage']:
            im_value = value
            im_name = 'imagename'
        immath_args[im_name] = im_value

    if name in ['mode', 'inpimage', 'inpmask', 'output', 'overwrite']:
        makemask_args[name] = value

if 'expr' in immath_args:
    task = crasa.CasaTask("immath", **immath_args)
    task.run()

if 'inpmask' not in makemask_args:
    makemask_args['inpmask'] = immath_args['outfile']

task = crasa.CasaTask(config.binary, **makemask_args)
task.run()
