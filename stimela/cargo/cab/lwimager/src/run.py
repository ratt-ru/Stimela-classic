import pyrap.images
import os
import sys
from pyrap.tables import table
from MSUtils import msutils
import tempfile
import astropy.io.fits as pyfits
import subprocess
import shlex
import shutil
import yaml


CONFIG = os.environ['CONFIG']
OUTPUT = os.environ['OUTPUT']
INPPUT = os.environ['INPUT']
MSDIR = os.environ['MSDIR']

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

params = cab['parameters']

tdir = tempfile.mkdtemp(dir='.')
os.chdir(tdir)


def rm_fr(item):
    os.system('rm -fr {}'.format(item))


def _run(prefix=None, predict=False, **kw):

    port2fits = kw.pop('port2fits', True)
    keep_casa_images = kw.pop('keep_casa_images', False)

    if predict:
        args = ['{0}={1}'.format(a, b) for a, b in kw.iteritems()]
        _runc = " ".join([cab["binary"]] + args)
        subprocess.check_call(shlex.split(_runc))
        return

    if kw.get('niter', 0) > 0:
        if kw.get('operation', None) not in ['clark', 'hogbom', 'csclean', 'multiscale', 'entropy']:
            kw['operation'] = 'csclean'
        images = {
            "restored":   ['{0}.restored.{1}'.format(prefix, a) for a in ['fits', 'img']],
            "model":   ['{0}.model.{1}'.format(prefix, a) for a in ['fits', 'img']],
            "residual":   ['{0}.residual.{1}'.format(prefix, a) for a in ['fits', 'img']],
        }

    elif kw.get('niter', 0) == 0:
        kw["operation"] = 'image'

        images = {
            "image":   ['{0}.dirty.{1}'.format(prefix, a) for a in ['fits', 'img']],
        }

    for key, value in images.iteritems():
        kw[key] = value[1]

    args = ['{0}={1}'.format(a, b) for a, b in kw.iteritems()]
    _runc = " ".join([cab["binary"]] + args)
    subprocess.check_call(shlex.split(_runc))

    if port2fits:
        print('Converting CASA iamges to FITS images')
        for fits, img in images.itervalues():
            im = pyrap.images.image(img)
            im.tofits(fits, overwrite=True, velocity=kw.get(
                'prefervelocity', False))
            if not keep_casa_images:
                rm_fr(img)


def predict_vis(msname, image, column="MODEL_DATA",
                chanchunk=None, chanstart=0, chanstep=1):
    """Converts image into predicted visibilities"""

    # CASA to convert them
    casaimage = '{0}/{1}.img'.format(OUTPUT, os.path.basename(image))

    # convert to CASA image
    img = pyrap.images.image(image)
    img.saveas(casaimage)

    imgshp = img.shape()
    ftab = table(msname+'/SPECTRAL_WINDOW')
    numchans = ftab.getcol('NUM_CHAN')[0]
    # default chunk list is entire chanel range. Update this if needed
    chunklist = [(0, numchans, None, None)]
    if len(imgshp) == 4 and imgshp[0] > 1:
        nimgchan = imgshp[0]

        print("image cube has {0} channels, MS has {1} channels".format(
            nimgchan, numchans))

        imgchansize = imgshp[1]*imgshp[2]*imgshp[3] * \
            4  # size of an image channel in bytes
        if chanchunk is None:
            mem_bytes = os.sysconf('SC_PAGE_SIZE') * \
                os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
            chanchunk = max((mem_bytes/20)/imgchansize, 1)
            print("based on available memory ({0}), max image chunk is {1} channels".format(
                mem_bytes, chanchunk))
        if chanchunk < nimgchan:
            mschanstep = numchans*chanstep/nimgchan
            if numchans % nimgchan:
                print(
                    "MS channels not evenly divisible into $nimgchan image channels, chunking may be incorrect")
            chunklist = []
            for chan0 in range(0, nimgchan, chanchunk):
                imch0, imch1 = chan0, (min(chan0+chanchunk, nimgchan)-1)
                msch0 = chanstart + imch0*mschanstep
                msnch = (imch1-imch0+1)*mschanstep/chanstep
                # overlap each chunk from 1 onwards by a half-chunk back to take care of extrapolated visibilties
                # from previous channel
                if imch0:
                    imch0 -= 1
                    msch0 -= mschanstep/2
                    msnch += mschanstep/2
                print("image chunk {0}~{1} corresponds to MS chunk {2}~{3}".format(
                    imch0, imch1, msch0, msch0+msnch-1))
                chunklist.append((msch0, msnch, imch0, imch1))

    # even in fill-model mode where it claims to ignore image parameters, the image channelization
    # arguments need to be "just so" as per below, otherwise it gives a GridFT: weights all zero message
    kw0 = {}
    kw0.update(ms=msname, model=casaimage,
               niter=0, fixed=1, mode="channel", operation="csclean",
               img_nchan=1, img_chanstart=chanstart, img_chanstep=numchans*chanstep)
    kw0['fillmodel'] = 1

    blc = [0]*len(imgshp)
    trc = [x-1 for x in imgshp]

    # now loop over image frequency chunks
    for ichunk, (mschanstart, msnumchans, imgch0, imgch1) in enumerate(chunklist):
        if len(chunklist) > 1:
            blc[0], trc[0] = imgch0, imgch1
            print("writing CASA image for slice {0} {1}".format(blc, trc))
            casaimage1 = "{0}.{1}.img".format(image, ichunk)
            rm_fr(casaimage1)
            print("writing CASA image for slice {0} {1} to {2}".format(
                blc, trc, casaimage1))
            img.subimage(blc, trc, dropdegenerate=False).saveas(casaimage1)
            kw0.update(model=casaimage1)
        else:
            img.unlock()
        # setup imager options
        kw0.update(chanstart=mschanstart, chanstep=chanstep, nchan=msnumchans)
        print("predicting visibilities into MODEL_DATA")

        _run(predict=True, **kw0)
        if len(chunklist) > 1:
            rm_fr(casaimage1)
    rm_fr(casaimage)

    if column != "MODEL_DATA":
        print('Data was predicted to MODEL_DATA column. Will now copy it to the {} column as requested'.format(column))
        msutils.copycol(msname=msname, fromcol="MODEL_DATA", tocol=column)


options = {}
for param in params:
    value = param['value']
    name = param['name']

    if name == 'prefix':
        prefix = value
        continue

    if value is None:
        continue
    if name == 'cellsize':
        if isinstance(value, (float, int)):
            value = '{}arcsec'.format(value)
    elif name in ['threshold', 'targetflux']:
        if isinstance(value, float):
            value = '{}arcsec'.format(value)
    options[name] = value

noise_image = options.pop('noise_image', False)
if noise_image:
    noise_sigma = options.pop('noise_sigma')
    noise_hdu = pyfits.open(noise_image)
    noise_data = noise_hdu[0].data
    noise_std = noise_data.std()
    threshold = noise_sigma*noise_std
    options['threshold'] = '{}Jy'.format(threshold)
else:
    options.pop('noise_sigma')

predict = options.pop('simulate_fits', False)
if predict:
    tfile = tempfile.NamedTemporaryFile(suffix='.fits')
    tfile.flush()
    cell = options.get('cellsize', None)
    if cell is None:
        with pyfits.open(predict) as _hdu:
            if hasattr(_hdu, '__iter__'):
                hdu = _hdu[0]
            else:
                hdu = _hdu

            cdelt = hdu.header.get('CDELT1', None)
            if cdelt:
                cell = '{:f}arcsec'.format(abs(cdelt)*3600)

    if cell is None:
        raise RuntimeError('The size of a pixel in this FITS image was not specified \
in FITS header (CDELT1/2), or as parameter for this module ("cellsize"). Cannot proceed')

    _runc = " ".join(['python /scratch/code/predict_from_fits.py'] + [predict, options['ms'], cell,
                                                             tfile.name])
    subprocess.check_call(shlex.split(_runc))
    predict_vis(msname=options['ms'], image=tfile.name, column=options.get('data', 'MODEL_DATA'),
                chanchunk=options.get('chanchunk', None), chanstart=options.get('img_chanstart', 0),
                chanstep=options.get('img_chanstep', 1))
    tfile.close()
else:
    _run(prefix, **options)

os.chdir(OUTPUT)
os.system('rm -r {}'.format(tdir))
