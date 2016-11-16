import astropy.io.fits as fitsio
import astropy.stats as stats
import numpy
import sys
import os
import concurrent.futures as cf

sys.path.append('/utils')
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]

jdict = utils.readJson(CONFIG)
image = jdict["image"]
sigma = jdict.get("sigma", 5)
iters = jdict.get("iters", 3)
kernel = jdict.get("kernel", 11)
overlap = jdict.get("overlap", 0.2)
mask_value = jdict.get("mask_value", 0)

outname = jdict.get("outname", None) or image[:-5]+"-masked.fits" 

outname = utils.substitute_globals(outname) or "%s/%s"%(INPUT, outname)
image = utils.substitute_globals(image) or "%s/%s"%(INPUT, image)

hdu = fitsio.open(image)
data = hdu[0].data
hdr = hdu[0].header
npix = hdr["NAXIS1"]

im = data[utils.get_imslice(hdr["naxis"])]

size = npix/kernel
overlap = int(size*overlap/2)
mask = numpy.zeros(im.shape, dtype=numpy.float32)

ex = cf.ProcessPoolExecutor(8)
futures = []

def work(i):
    slice_list = []
    for j in xrange(kernel):
        xi, yi = i*size-overlap, j*size-overlap
        xf, yf = i*size + size + overlap, j*size + size + overlap

        xi, xf = sorted([xi,xf])
        yi, yf = sorted([yi,yf])

        # Boundary conditions
        if xi <0: 
            xi = 0 
        if yi < 0:
            yi = 0 

        if xf > npix:
            xf = npix
        if yf > npix:
            yf = npix
    
        imslice = [slice(xi, xf), slice(yi, yf)]
        tmp = im[imslice]
        slice_list.append([i, imslice, stats.sigma_clip(tmp, sigma=sigma, iters=iters).mask])
    return slice_list

for i in xrange(kernel):
    f = ex.submit(work, i)
    futures.append(f)

for i, f in enumerate(cf.as_completed(futures)):
    for j, imslice, submask in f.result():
        mask[imslice] = submask

if mask_value != 0:
    if isinstance(mask_value, (str, unicode)):
        if str(mask_value).lower()=="nan":
            mask_value = numpy.nan
    mask[mask==0] = mask_value

hdu[0].data = mask[numpy.newaxis, numpy.newaxis, ...]

hdu.writeto(outname, clobber=True)
hdu.close()
