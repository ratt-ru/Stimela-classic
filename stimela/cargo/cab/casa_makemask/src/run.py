import os
import sys 
import logging
import Crasa.Crasa as crasa
import yaml
import glob
import shutil

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

makemask_args = {}
immath_args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

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

task = crasa.CasaTask(cab["binary"], **makemask_args)
try:
    task.run()
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)

