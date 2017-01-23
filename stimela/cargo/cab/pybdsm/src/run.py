import os
import sys
import re
from lofar import bdsm
import numpy
import Tigger
import tempfile
import pyfits

from astLib.astWCS import WCS
from Tigger.Models import SkyModel, ModelClasses


sys.path.append('/utils')
import utils

CONFIG = os.environ['CONFIG']
INPUT = os.environ['INPUT']
OUTPUT = os.environ['OUTPUT']
MSDIR = os.environ['MSDIR']

cab = utils.readJson(CONFIG)

write_catalog = ['bbs_patches', 'bbs_patches_mask',
            'catalog_type', 'clobber', 'correct_proj', 'format', 
            'incl_chan', 'incl_empty', 'srcroot', 'port2tigger', 'outfile']

img_opts = {}
write_opts = {}

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    if name in write_catalog:
        write_opts[name] = value
    else:
        img_opts[name] = value

image = img_opts.pop('filename')
outfile = write_opts.pop('outfile')

img = bdsm.process_image(image, **img_opts)

port2tigger = write_opts.pop('port2tigger', False)

if write_opts.get('format', None) !='fits':
    write_opts['format'] = 'fits'

img.write_catalog(outfile=outfile, **write_opts)

if not port2tigger:
    sys.exit(0)

# convert to Gaul file to Tigger LSM
# First make dummy tigger model
tfile = tempfile.NamedTemporaryFile(suffix='.txt')
tfile.flush()

prefix = outfile[:-5]
tname_lsm = prefix + ".lsm.html"
with open(tfile.name, "w") as stdw:
    stdw.write("#format:name ra_d dec_d i emaj_s emin_s pa_d\n")

model = Tigger.load(tfile.name)
tfile.close()

def tigger_src(src, idx):

    name = "SRC%d"%idx

    flux = ModelClasses.Polarization(src["Total_flux"], 0, 0, 0, I_err=src["E_Total_flux"])

    ra, ra_err = map(numpy.deg2rad, (src["RA"], src["E_RA"]) )
    dec, dec_err = map(numpy.deg2rad, (src["DEC"], src["E_DEC"]) )
    pos =  ModelClasses.Position(ra, dec, ra_err=ra_err, dec_err=dec_err)

    ex, ex_err = map(numpy.deg2rad, (src["DC_Maj"], src["E_DC_Maj"]) )
    ey, ey_err = map(numpy.deg2rad, (src["DC_Min"], src["E_DC_Min"]) )
    pa, pa_err = map(numpy.deg2rad, (src["PA"], src["E_PA"]) )

    if ex and ey: 
        shape = ModelClasses.Gaussian(ex, ey, pa, ex_err=ex_err, ey_err=ey_err, pa_err=pa_err)
    else:
        shape = None

    return SkyModel.Source(name, pos, flux, shape=shape)


with pyfits.open(outfile) as hdu:
    data = hdu[1].data

    for i, src in enumerate(data):
        model.sources.append(tigger_src(src, i)) 

wcs = WCS(image)
centre = wcs.getCentreWCSCoords()
model.ra0, model.dec0 = map(numpy.deg2rad, centre)

model.save(tname_lsm)
# Rename using CORPAT
utils.xrun("tigger-convert", [tname_lsm, "--rename -f"])
