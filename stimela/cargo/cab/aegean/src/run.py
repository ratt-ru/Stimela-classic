import os
import sys
import numpy
import Tigger
import tempfile
import pyfits
import shutil
import shlex
import subprocess
import yaml
import glob

from astLib.astWCS import WCS
from astropy.table import Table
from Tigger.Models import SkyModel, ModelClasses

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)
junk = cab["junk"]

write_catalog = ['port2tigger', 'table']

write_opts = {}
img_opts = {}

args = []

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    if value is None:
        continue
    elif value is False:
        continue
    if name == 'filename':  # positional argument
        args += ['{0}'.format(value)]
    else:
        if name != "port2tigger":
            args += ['{0}{1} {2}'.format(cab['prefix'], name, value)]
    if name in write_catalog:
        write_opts[name] = value
    else:
        img_opts[name] = value

_runc = " ".join([cab["binary"]] + args)

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
                # Leave other types

port2tigger = write_opts.pop('port2tigger')
outfile = write_opts.pop('table')
image = img_opts.pop('filename')

if port2tigger:
    write_opts['format'] = 'fits'

if not port2tigger:
    sys.exit(0)


# convert to data file to Tigger LSM
# First make dummy tigger model
tfile = tempfile.NamedTemporaryFile(suffix='.txt')
tfile.flush()

prefix = os.path.splitext(outfile)[0]
tname_lsm = prefix + ".lsm.html"
with open(tfile.name, "w") as stdw:
    stdw.write("#format:name ra_d dec_d i emaj_s emin_s pa_d\n")

model = Tigger.load(tfile.name)
tfile.close()


def tigger_src(src, idx):

    name = "SRC%d" % idx
    flux = ModelClasses.Polarization(float(src["int_flux"]), 0, 0, 0,
                                     I_err=float(src["err_int_flux"]))
    ra, ra_err = map(numpy.deg2rad, (float(src["ra"]), float(src["err_ra"])))
    dec, dec_err = map(numpy.deg2rad, (float(src["dec"]),
                                       float(src["err_dec"])))
    pos = ModelClasses.Position(ra, dec, ra_err=ra_err, dec_err=dec_err)
    ex, ex_err = map(numpy.deg2rad, (float(src["a"]), float(src["err_a"])))
    ey, ey_err = map(numpy.deg2rad, (float(src["b"]), float(src["err_b"])))
    pa, pa_err = map(numpy.deg2rad, (float(src["pa"]), float(src["err_pa"])))

    if ex and ey:
        shape = ModelClasses.Gaussian(
            ex, ey, pa, ex_err=ex_err, ey_err=ey_err, pa_err=pa_err)
    else:
        shape = None
    source = SkyModel.Source(name, pos, flux, shape=shape)
    # Adding source peak flux (error) as extra flux attributes for sources,
    # and to avoid null values for point sources I_peak = src["Total_flux"]
    if shape:
        source.setAttribute("I_peak", float(src["peak_flux"]))
        source.setAttribute("I_peak_err", float(src["err_peak_flux"]))
    else:
        source.setAttribute("I_peak", float(src["int_flux"]))
        source.setAttribute("I_peak_err", float(src["err_int_flux"]))

    return source


data = Table.read('{0}_comp.{1}'.format(outfile.split('.')[0], outfile.split('.')[-1]),
                  format=outfile.split('.')[-1])

for i, src in enumerate(data):

    model.sources.append(tigger_src(src, i))

wcs = WCS(image)
centre = wcs.getCentreWCSCoords()
model.ra0, model.dec0 = map(numpy.deg2rad, centre)

model.save(tname_lsm)
# Rename using CORPAT
subprocess.check_call(["tigger-convert", tname_lsm, "--rename", "-f"])
