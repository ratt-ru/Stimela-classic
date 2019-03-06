import os
import sys
import Tigger

sys.path.append('/scratch/stimela')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
args = []
msname = None

sofia_file = 'sofia_parameters.par'
wstd = open(sofia_file, 'w')

wstd.write('writeCat.outputDir={:s}\n'.format(OUTPUT))

for param in cab['parameters']:
    name = param['name']
    value = param['value']
    
    if value is None:
        continue
    print name, value
	
    wstd.write('{0}={1}\n'.format(name, value))

wstd.close()

utils.xrun('sofia_pipeline.py', [sofia_file])

port2tigger = write_opts.pop('port2tigger')
outfile = write_opts.pop('table')
image = img_opts.pop('filename')

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
    flux = ModelClasses.Polarization(float(src["f_int"]), 0, 0, 0))
    ra = map(numpy.deg2rad, (float(src["ra"])))
    dec = map(numpy.deg2rad, (float(src["dec"])))
    pos = ModelClasses.Position(ra, dec)
    ex = map(numpy.deg2rad, (float(src["ell_maj"])))
    ey = map(numpy.deg2rad, (float(src["ell_min"])))
    pa = map(numpy.deg2rad, (float(src["ell_pa"])))

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

data = Table.read('{0}_cat.{1}'.format(outfile.split('.')[0], 'ascii'),
                  format=outfile.split('.')[-1])

for i, src in enumerate(data):

    model.sources.append(tigger_src(src, i))

wcs = WCS(image)
centre = wcs.getCentreWCSCoords()
model.ra0, model.dec0 = map(numpy.deg2rad, centre)

model.save(tname_lsm)
# Rename using CORPAT
utils.xrun("tigger-convert", [tname_lsm, "--rename -f"])
