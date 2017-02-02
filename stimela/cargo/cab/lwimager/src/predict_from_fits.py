import pyfits as fitsio
import numpy
from pyrap.tables import table
import numpy
import os
import sys
import tempfile

sys.path.append('/utils')
import utils

imagename = sys.argv[1]
msname = sys.argv[2]
cell = sys.argv[3]

hdulist = fitsio.open(imagename)
if isinstance(hdulist, list):
    hdu = hdulist[0]
else:
    hdu = hdulist

tfile = tempfile.NamedTemporaryFile(suffix='.fits')
tfile.flush()

nchan = hdu.data.shape[0]
sys.stdout.write('Creating template image')
os.system('rm -fr {0}'.format(tfile.name))
utils.xrun('lwimager', ['ms='+msname, 'fits='+tfile.name, 'data=psf', 'npix=64',
                        'mode=mfs', 'nchan={:d}'.format(nchan), 'img_nchan={:d}'.format(nchan),
                        'prefervelocity=False', 'cellsize={0}'.format(cell)])

sys.stdout.write('Created template image. Will now proceed to simulate FITS model into MS')


with fitsio.open(tfile.name) as hdu0:
    header = hdu0[0].header

tfile.close()

naxis = hdu.header['NAXIS']
raNpix = hdu.header['NAXIS1']
decNpix = hdu.header['NAXIS2']

header['CRPIX1'] = raNpix/2.0
header['CRPIX2'] = decNpix/2.0

if naxis == 2:
    hdu.data = hdu.data[numpy.newaxis,numpy.newaxis,...]

if naxis == 3:
    hdu.data = hdu.data[:,numpy.newaxis,...]

hdu.header = header

hdulist.writeto(sys.argv[4], clobber=True)
