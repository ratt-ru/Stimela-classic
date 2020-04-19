import os
import sys
import subprocess
import shlex
import shutil
import glob
import yaml

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    args[name] = value

if os.path.exists(OUTPUT+'/mask_mosaic') == False:
    os.mkdir(OUTPUT+'/mask_mosaic')

outdir = OUTPUT+'/mask_mosaic'

try:
    make_table = " ".join(['mImgtbl', args['input_dir'], outdir+'/mosaic_table.tbl'])
    subprocess.check_call(shlex.split(make_table))

    make_header = " ".join(['mMakeHdr', outdir +
               '/mosaic_table.tbl', outdir+'/mosaic_header.hdr'])
    subprocess.check_call(shlex.split(make_header))

    project_mosaic = " ".join(['mProjExec', '-p', args['input_dir'], outdir +
                  '/mosaic_table.tbl', outdir+'/mosaic_header.hdr', outdir, outdir+'/stats.tbl'])
    subprocess.check_call(shlex.split(project_mosaic))

    make_mosaic_table = ['mImgtbl', outdir, outdir+'/mosaic_table2.tbl']
    subprocess.check_call(shlex.split(make_mosaic_table))

    _runc = " ".join(['mAdd', '-p', args['input_dir'], outdir +
               '/mosaic_table2.tbl', outdir+'/mosaic_header.hdr', OUTPUT+'/mosaic.fits'])
    subprocess.check_call(shlex.split(_runc))
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
                # Leave other types
