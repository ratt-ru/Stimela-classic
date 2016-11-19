import sys
import numpy
import pyfits
import scipy.stats as stats



def get_imslice(ndim):
    imslice = []
    for i in xrange(ndim):
        if i<ndim-2:
            imslice.append(0)
        else:
            imslice.append(slice(None))

    return imslice


def fitsFreqInd(hdr):
    ndim = hdr["naxis"]
    keys = [hdr["CTYPE%d"%d].strip().lower() for d in xrange(1,ndim+1)]

    if "freq" not in keys:
        return False

    ind = keys.index("freq") + 1

    return ind


def freqInfo(fits):
    with pyfits.open(fits) as hdu:
        hdr = hdu[0].header
        ndim = hdr["NAXIS"]

    ind = fitsFreqInd(hdr)
    ref_freq = hdr["CRVAL%d"%ind]
    dfreq = hdr["CDELT%d"%ind]
    nchan = hdr["NAXIS%d"%ind]
    ref_chan = hdr["CRPIX%d"%ind]

    cnt_freq = ref_freq + (nchan/2 - ref_chan) * dfreq
    bw = dfreq*nchan

    freqs = numpy.linspace(cnt_freq-bw/2, cnt_freq+bw/2, nchan)

    return freqs, cnt_freq, bw, nchan, ind


def spifit(cube, prefix=None, mask=None, thresh=None,
           sigma=20, spi_image=None,
           spi_err_image=None):

    if isinstance(cube, (list, tuple)):
        ims = []
        nchan = len(cube)
        freqs = []
        prefix = prefix or cube[0][-3:]

        for im in cube:
            with pyfits.open(im) as hdu:
                hdr = hdu[0].header
                hdu_data = hdu[0].data
                ndim = hdr["NAXIS"]
                ind = fitsFreqInd(hdr)
                freqs.append( hdr["CRVAL%d"%ind])
                ims.append( hdu_data[get_imslice(ndim)]  )

        data = numpy.dstack(ims).T
        ndim = data.ndim
        cnt_freq = freqs[nchan/2]

    else:
        prefix = prefix or cube[-3:]
        with pyfits.open(cube) as hdu:
            data = hdu[0].data
            hdr = hdu[0].header
            ndim = data.ndim

        freqs, cnt_freq, bw, nchan, ind = freqInfo(cube)

    freq_ind = ndim - ind
    imslice = get_imslice(ndim)
    imslice[freq_ind] = slice(None)
    data = data[imslice]

    mfs = numpy.mean(data, axis=0)
    alpha = numpy.zeros(mfs.shape, dtype=numpy.float32)
    err = numpy.zeros(mfs.shape, dtype=numpy.float32)
    aa = []
    bb = []
    I0 = []

    if mask:
        with pyfits.open(mask) as hdu:
            mdata = hdu[0].data
            mndim = mdata.ndim
            mask = mdata[get_imslice(mndim)]

        ind = numpy.where(numpy.logical_and(mask>1e-33, mfs>1e-8))
    else:
        if thresh in [None, 0]:
            noise = numpy.median( abs(mfs - numpy.median(mfs))  )/0.667
            thresh = sigma*noise
        ind = numpy.where(mfs>thresh)

    if len(ind) < 1:
        raise RunTimeError("No pixels above set threshold, or outside masked region")

    for i,j in zip(ind[0], ind[1]):
        x = numpy.log(numpy.array(freqs)/cnt_freq)
        val = data[:,i,j]
        if val.any() <= 0:
            continue

        y = numpy.log( val )

        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

        alpha[i,j] = slope
        err[i,j] = std_err

    #    aa.append(intercept)
    #    bb.append(std_err)
    #    I0.append(numpy.log(data[nchan/2,i,j]))

    nans = numpy.isnan(alpha)
    alpha[nans] = 0.0
    err[nans] = 1e99
    
    pyfits.writeto(spi_image or prefix+".alpha.fits", alpha, hdr, clobber=True)
    pyfits.writeto(spi_err_image or prefix+".alpha.err.fits", err, hdr, clobber=True)
