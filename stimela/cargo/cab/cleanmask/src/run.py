import astropy.io.fits as fitsio
import astropy.stats as stats
import numpy
import sys
import os
import concurrent.futures as cf
from skimage import measure
import scipy.ndimage as ndimage

morph = ndimage.morphology

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
diter = jdict.get("diter", 50)
tol = jdict.get("tol", 0.05)
dilate = jdict.get("dilate", True)
include_negatives = jdict.get("include_negatives", False)

outname = jdict.get("outname", None) or image[:-5]+"-masked.fits" 

image = utils.substitute_globals(image) or INPUT + "/" + image
outname = utils.substitute_globals(image) or OUTPUT + "/" + outname

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

print "Creating mask..."
for i in xrange(kernel):
    f = ex.submit(work, i)
    futures.append(f)

for i, f in enumerate(cf.as_completed(futures)):
    for j, imslice, submask in f.result():
        mask[imslice] = submask

if not include_negatives:
    mask[im<0] = 0

islands = measure.label(mask, background=0)
labels = set(islands.flatten())
labels.remove(0)

centre = lambda island : map(int, [island[0].mean(), island[1].mean()])
def extent(isl):
    nisl = len(isl[0])
    r = []
    for i in xrange(nisl):
        for j in xrange(i,nisl):
            a = isl[0][i], isl[1][i]
            b = isl[0][j], isl[1][j]
            rad = (a[0]-b[0])**2 + (a[1]-b[1])**2
            r.append(int(rad**0.5))
    return max(r)

if dilate:
    print "Dilating mask..."
    for label in labels:
        island = numpy.where(islands==label)
        rx, ry = centre(island)
        size = int(extent(island) * 1.5)
        xi, yi = rx - size, ry - size
        xf, yf = rx + size, ry + size
    
        if xi <0: 
            xi = 0 
        if yi < 0:
            yi = 0 
    
        if xf > npix:
            xf = npix
        if yf > npix:
            yf = npix
    
        imslice = [slice(xi, xf), slice(yi, yf)]
        imask = mask[imslice]
        iim = im[imslice]
    
        f0 = (iim*imask).sum()
        make_bigger = f0 > 0.0
        struct = ndimage.generate_binary_structure(2, 2)
        counter = 0
        nmask = morph.binary_dilation(imask, structure=struct, iterations=2).astype(imask.dtype)

        while make_bigger:
            f1 = (iim*nmask).sum()
            df = abs(f0-f1)/f0
            if df<tol or df <=0:
                make_bigger = False
            counter += 1
            if counter>diter:
                make_bigger = False
    
            dilate += 2
            struct = ndimage.generate_binary_structure(2, 2)
            if make_bigger:
                nmask = morph.binary_dilation(nmask, structure=struct, iterations=3).astype(imask.dtype)
        mask[imslice] = nmask

if mask_value != 0:
    if isinstance(mask_value, (str, unicode)):
        if str(mask_value).lower()=="nan":
            mask_value = numpy.nan
    mask[mask==0] = mask_value

hdu[0].data = mask[numpy.newaxis, numpy.newaxis, ...]

hdu.writeto(outname, clobber=True)
hdu.close()
