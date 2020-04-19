import pyfits as fitsio
import numpy
from pyrap.tables import table
import numpy
import os
import sys
import tempfile
import subprocess
import shlex

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
sys.stdout.write('Creating template image\n')
os.system('rm -fr {0}'.format(tfile.name))
_runc = " ".join(['lwimager'] + ['ms='+msname, 'fits='+tfile.name, 'data=psf', 'npix=64',
                        'mode=mfs', 'nchan={:d}'.format(
                            nchan), 'img_nchan={:d}'.format(nchan),
                        'prefervelocity=False', 'cellsize={0}'.format(cell)])
subprocess.check_call(shlex.split(_runc))

sys.stdout.write(
    'Created template image. Will now proceed to simulate FITS model into MS\n')


with fitsio.open(tfile.name) as hdu0:
    header = hdu0[0].header

tfile.close()

naxis = hdu.header['NAXIS']
raNpix = hdu.header['NAXIS1']
decNpix = hdu.header['NAXIS2']

header['CRPIX1'] = raNpix/2.0
header['CRPIX2'] = decNpix/2.0

if naxis < 2:
    raise RuntimeError('FITS image has to have at least two axes')

elif naxis == 2:
    hdu.data = hdu.data[numpy.newaxis, numpy.newaxis, ...]
    sys.stdout.write(
        'WARNING::FITS image has 2 axes. Will add STOKES and FREQ axes\n')
elif naxis == 3:
    sys.stdout.write('WARNING::FITS image has 3 axes.\n')
    # Try to find out what is the 3rd axis
    third_axis = hdu.header.get('CTYPE3', None)
    if third_axis is None:
        sys.stdout.write(
            'WARNING:: Third axis is not labelled, assuming its the FREQ Axis\n')
        hdu.data = hdu.data[:, numpy.newaxis, ...]
    elif third_axis.lower() == 'freq':
        hdu.data = hdu.data[:, numpy.newaxis, ...]
    elif third_axis.lower() == 'stokes':
        hdu.data = hdu.data[numpy.newaxis, ...]
    else:
        sys.stdout.write(
            'WARNING:: CTYPE3 value [{}] is unknown, will ignore it and assume 3rd axis is FREQ\n'.format(third_axis))
        hdu.data = hdu.data[:, numpy.newaxis, ...]

elif naxis == 4:
    sys.stdout.write(
        'FITS image has four axes. If the axes are labeled (via CTYPE<axis index>), will attempt to restructure it so it is fit to predict from\n')
    third_axis = hdu.header.get('CTYPE3', None)
    if third_axis is None:
        raise RuntimeError(
            'ABORT:: FITS axes are not labelled. Cannot proceed. Please label STOKES and FREQ accordingly\n')
    elif third_axis.lower() == 'freq':
        hdu.data = numpy.rollaxis(hdu.data, 1)
else:
    sys.stdout.write(
        'WARNING:: FITS image has more than 4 axes. Passing the  buck to lwimger\n')


hdu.header = header

hdulist.writeto(sys.argv[4], clobber=True)
