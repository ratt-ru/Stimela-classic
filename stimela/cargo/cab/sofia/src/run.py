import os
import sys
import Tigger
import numpy
import tempfile
import json
import codecs
import shlex
import shutil
import glob
import subprocess

from astLib.astWCS import WCS
from Tigger.Models import SkyModel, ModelClasses


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

with codecs.open(CONFIG, "r", "utf8") as stdr:
    cab = json.load(stdr)

junk = cab["junk"]
args = []
msname = None

sofia_file = 'sofia_parameters.par'
wstd = open(sofia_file, 'w')

wstd.write('writeCat.outputDir={:s}\n'.format(OUTPUT))
port2tigger = False
image = None
writecat = False
parameterise = False

for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue
    if name == "port2tigger":
        port2tigger = value
        continue
    if name == "steps.doWriteCat":
        writecat = value
    if name == "steps.doParameterise":
        parameterise = value
    if name == "import.inFile":
        image = value

    wstd.write('{0}={1}\n'.format(name, value))

wstd.close()

_runc = " ".join(['sofia_pipeline.py', sofia_file])

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

if not port2tigger:
    sys.exit(0)

# convert to data file to Tigger LSM
# First make dummy tigger model
tfile = tempfile.NamedTemporaryFile(suffix='.txt')
tfile.flush()

if image and writecat and parameterise:
    pass
else:
    sys.exit(0)

prefix = os.path.splitext(image)[0]
tname_lsm = prefix + ".lsm.html"
with open(tfile.name, "w") as stdw:
    stdw.write("#format:name ra_d dec_d i emaj_s emin_s pa_d\n")

model = Tigger.load(tfile.name)
tfile.close()


def tigger_src(src, idx):

    name = "SRC%d" % idx
    flux = ModelClasses.Polarization(src["f_int"], 0, 0, 0)
    ra = numpy.deg2rad(src["ra"])
    dec = numpy.deg2rad(src["dec"])
    pos = ModelClasses.Position(ra, dec)
    ex = numpy.deg2rad(src["ell_maj"])
    ey = numpy.deg2rad(src["ell_min"])
    pa = numpy.deg2rad(src["ell_pa"])

    if ex and ey:
        shape = ModelClasses.Gaussian(ex, ey, pa)
    else:
        shape = None
    source = SkyModel.Source(name, pos, flux, shape=shape)
    # Adding source peak flux (error) as extra flux attributes for sources,
    # and to avoid null values for point sources I_peak = src["Total_flux"]
    if shape:
        source.setAttribute("I_peak", float(src["f_peak"]))
    else:
        source.setAttribute("I_peak", float(src["f_int"]))

    return source


with open('{0}_cat.ascii'.format(prefix)) as stdr:
    # Header
    stdr.readline()
    # Column names
    names = stdr.readline().split("#")[1].strip().split()
    # Units
    stdr.readline()
    # Column numbers
    stdr.readline()
    sys.stdout.write(" ".join(names))
    data = numpy.genfromtxt(stdr,
                            names=names + ["col"])

for i, src in enumerate(data):
    model.sources.append(tigger_src(src, i))

wcs = WCS(image)
centre = wcs.getCentreWCSCoords()
model.ra0, model.dec0 = map(numpy.deg2rad, centre)

model.save(tname_lsm)
# Rename using CORPAT
utils.xrun("tigger-convert", [tname_lsm, "--rename -f"])
