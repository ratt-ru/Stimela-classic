import os
import sys
import subprocess
sys.path.append('/scratch/stimela')
import utils
#import montage_wrapper as montage


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    #if name == "output_dir":
    #    args["output_dir"] = os.path.join(OUTPUT, value)
    #if name == 'input_dir':
    #    args['input_dir'] = os.path.join(INPUT,value)
    args[name] = value

if os.path.exists(OUTPUT+'/mask_mosaic')==False:
    os.mkdir(OUTPUT+'/mask_mosaic')

outdir = OUTPUT+'/mask_mosaic'


make_table = ['mImgtbl',args['input_dir'],outdir+'/mosaic_table.tbl'] 
subprocess.check_output(make_table)

make_header = ['mMakeHdr',outdir+'/mosaic_table.tbl',outdir+'/mosaic_header.hdr']
subprocess.check_output(make_header)

project_mosaic = ['mProjExec', '-p',args['input_dir'],outdir+'/mosaic_table.tbl',outdir+'/mosaic_header.hdr',outdir,outdir+'/stats.tbl']
subprocess.check_output(project_mosaic)

make_mosaic_table = ['mImgtbl',outdir,outdir+'/mosaic_table2.tbl']
subprocess.check_output(make_mosaic_table)

make_mosaic=['mAdd', '-p', args['input_dir'], outdir+'/mosaic_table2.tbl',outdir+'/mosaic_header.hdr',OUTPUT+'/mosaic.fits']
subprocess.check_output(make_mosaic)

#command = 'mProjExec '+OUTPUT+'/mosaic_table.tbl '+OUTPUT+'/mosaic_header.hdr '+args['output_dir']+' '+OUTPUT+'/mosaic_stats.tbl'
#print command
#os.system(command)
