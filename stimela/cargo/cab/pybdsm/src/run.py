import os
import sys
import re
import bdsf as bdsm  # bdsm it is and bdsm it shall remain
import numpy
import Tigger
import tempfile
import astropy.io.fits as pyfits
import yaml
import shlex
import shutil
import glob
import subprocess

from astLib.astWCS import WCS
from Tigger.Models import SkyModel, ModelClasses

CONFIG = os.environ['CONFIG']
INPUT = os.environ['INPUT']
OUTPUT = os.environ['OUTPUT']
MSDIR = os.environ['MSDIR']

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

write_catalog = ['bbs_patches', 'bbs_patches_mask',
                 'catalog_type', 'clobber', 'correct_proj', 'format',
                 'incl_chan', 'incl_empty', 'srcroot', 'port2tigger', 'outfile']

img_opts = {}
write_opts = {}
# Spectral fitting parameters
freq0 = None
spi_do = False

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    if name in ['multi_chan_beam']:
        multi_chan_beam = value
        continue
    if name in write_catalog:
        write_opts[name] = value
    elif name in ['freq0', 'frequency']:
        freq0 = value
    else:
        img_opts[name] = value
        if name == 'spectralindex_do':
            spi_do = value

img_opts.pop('freq0', None)
if freq0 is None:
    with pyfits.open(img_opts['filename']) as hdu:
        hdr = hdu[0].header
        for i in range(1, hdr['NAXIS']+1):
            if hdr['CTYPE{0:d}'.format(i)].startswith('FREQ'):
                freq0 = hdr['CRVAL{0:d}'.format(i)]

if spi_do and multi_chan_beam:
    with pyfits.open(img_opts['filename']) as hdu:
        hdr = hdu[0].header
    beams = []
    # Get a sequence of BMAJ with digit suffix from the image header keys
    bmaj_ind = filter(lambda a: a.startswith('BMAJ')
                      and a[-1].isdigit(), hdr.keys())
    for bmaj in bmaj_ind:
        ind = bmaj.split('BMAJ')[-1]
        beam = [hdr['{0:s}{1:s}'.format(b, ind)]
                for b in 'BMAJ BMIN BPA'.split()]
        beams.append(tuple(beam))
    # parse beam info to pybdsm
    img_opts['beam_spectrum'] = beams

image = img_opts.pop('filename')
filename = os.path.basename(image)

outfile = write_opts.pop('outfile')

for key, value in sorted(img_opts.items()):
    sys.stderr.write("{:20}: {}\n".format(key, value))
sys.stderr.flush()


try:
    img = bdsm.process_image(image, **img_opts)

    port2tigger = write_opts.pop('port2tigger', True)

    if port2tigger:
        write_opts['format'] = 'fits'

    img.write_catalog(outfile=outfile, **write_opts)
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)

if not port2tigger:
    sys.exit(0)

# convert to Gaul file to Tigger LSM
# First make dummy tigger model
tfile = tempfile.NamedTemporaryFile(suffix='.txt')
tfile.flush()

prefix = os.path.splitext(outfile)[0]
tname_lsm = prefix + ".lsm.html"
with open(tfile.name, "w") as stdw:
    stdw.write("#format:name ra_d dec_d i q u v emaj_s emin_s pa_d\n")

model = Tigger.load(tfile.name)
tfile.close()


def tigger_src(src, idx):

    name = "SRC%d" % idx

    try:
        flux = ModelClasses.Polarization(src["Total_flux"], src["Total_Q"],
                                         src["Total_U"], src["Total_V"],
                                         I_err=src["E_Total_flux"],
                                         Q_err=src["E_Total_Q"],
                                         U_err=src["E_Total_U"],
                                         V_err=src["E_Total_V"])
    except KeyError:
        flux = ModelClasses.Polarization(src["Total_flux"], 0, 0, 0,
                                         I_err=src["E_Total_flux"])

    ra, ra_err = map(numpy.deg2rad, (src["RA"], src["E_RA"]))
    dec, dec_err = map(numpy.deg2rad, (src["DEC"], src["E_DEC"]))
    pos = ModelClasses.Position(ra, dec, ra_err=ra_err, dec_err=dec_err)
    ex, ex_err = map(numpy.deg2rad, (src["DC_Maj"], src["E_DC_Maj"]))
    ey, ey_err = map(numpy.deg2rad, (src["DC_Min"], src["E_DC_Min"]))
    pa, pa_err = map(numpy.deg2rad, (src["PA"], src["E_PA"]))

    if ex and ey:
        shape = ModelClasses.Gaussian(
            ex, ey, pa, ex_err=ex_err, ey_err=ey_err, pa_err=pa_err)
    else:
        shape = None
    source = SkyModel.Source(name, pos, flux, shape=shape)
    # Adding source peak flux (error) as extra flux attributes for sources,
    # and to avoid null values for point sources I_peak = src["Total_flux"]
    if shape:
        source.setAttribute("I_peak", src["Peak_flux"])
        source.setAttribute("I_peak_err", src["E_peak_flux"])
    else:
        source.setAttribute("I_peak", src["Total_flux"])
        source.setAttribute("I_peak_err", src["E_Total_flux"])

    if spi_do:
        # Check if start frequency is provided if not provided raise error.
        # It is used to define tigger source spectrum index frequency
        if freq0:
            spi, spi_err = (src['Spec_Indx'], src['E_Spec_Indx'])
            source.spectrum = ModelClasses.SpectralIndex(spi, freq0)
            source.setAttribute('spi_error', spi_err)
        else:
            raise RuntimeError("No start frequency (freq0) provided.")
    return source


with pyfits.open(outfile) as hdu:
    data = hdu[1].data

    for i, src in enumerate(data):
        model.sources.append(tigger_src(src, i))

wcs = WCS(image)
centre = wcs.getCentreWCSCoords()
model.ra0, model.dec0 = map(numpy.deg2rad, centre)

model.save(tname_lsm)
# Rename using CORPAT
_runc = "tigger-convert %s --rename -f" % tname_lsm
try:
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
