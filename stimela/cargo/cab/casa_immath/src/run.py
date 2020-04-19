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

unstack_params = ['unstack', 'nchans', 'keep_casa_images', 'port2fits']
unstack_args = {}
immath_args = {}


def rm_fr(item):
    os.system('rm -fr {}'.format(item))


for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    if name in unstack_params:
        unstack_args[name] = value
    else:
        immath_args[name] = value

unstack = unstack_args.pop(cab["binary"], False)

if not unstack:
    task = crasa.CasaTask("immath", **immath_args)
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
else:
    images = immath_args['imagename']
    for image in images:
        for i in range(unstack_args['nchans']):
            ext = image.split('.')[-1]
            chan_num = str(i)
            outfile = '{:s}-{:s}.{:s}'.format(
                immath_args['outfile'], chan_num, ext)
            run_immath_args = immath_args.copy()
            run_immath_args['imagename'] = image
            run_immath_args['outfile'] = outfile
            run_immath_args['chans'] = chan_num
            task = crasa.CasaTask(cab["binary"], **run_immath_args)
            task.run()
            if unstack_args['port2fits']:
                print('Converting CASA images to FITS images')
                fits = outfile + '.fits'
                task = crasa.CasaTask(
                    "exportfits", **dict(imagename=outfile, fitsimage=fits, overwrite=True))
                task.run()
                if not unstack_args['keep_casa_images']:
                    rm_fr(outfile)
