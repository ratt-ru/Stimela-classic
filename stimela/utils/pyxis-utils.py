# This is my pyxis tool box

import Pyxis
import pyfits
import numpy
import math
from pyrap.tables import table


def compute_vis_noise(sefd):
    """Computes nominal per-visibility noise"""

    tab = ms.ms()
    spwtab = ms.ms(subtable="SPECTRAL_WINDOW")

    freq0 = spwtab.getcol("CHAN_FREQ")[ms.SPWID, 0]
    wavelength = 300e+6/freq0
    bw = spwtab.getcol("CHAN_WIDTH")[ms.SPWID, 0]
    dt = tab.getcol("EXPOSURE", 0, 1)[0]
    dtf = (tab.getcol("TIME", tab.nrows()-1, 1)-tab.getcol("TIME", 0, 1))[0]

    # close tables properly, else the calls below will hang waiting for a lock...
    tab.close()
    spwtab.close()

    info(">>> $MS freq %.2f MHz (lambda=%.2fm), bandwidth %.2g kHz, %.2fs integrations, %.2fh synthesis"%(freq0*1e-6, wavelength, bw*1e-3, dt, dtf/3600))
    noise = sefd/math.sqrt(abs(2*bw*dt))
    info(">>> SEFD of %.2f Jy gives per-visibility noise of %.2f mJy"%(sefd, noise*1000))

    return noise 


def simnoise (noise=0, rowchunk=100000, 
              addToCol=None, scale_noise=1.0, 
              column='MODEL_DATA'):
    """ Simulate noise into an MS """

    spwtab = ms.ms(subtable="SPECTRAL_WINDOW")
    freq0 = spwtab.getcol("CHAN_FREQ")[ms.SPWID,0]/1e6

    tab = ms.msw()
    dshape = list(tab.getcol('DATA').shape)
    nrows = dshape[0]

    noise = noise or compute_vis_noise()

    if addToCol: colData = tab.getcol(addToCol)

    for row0 in range(0, nrows, rowchunk):
        nr = min(rowchunk, nrows-row0)
        dshape[0] = nr
        data = noise*(numpy.random.randn(*dshape) + 1j*numpy.random.randn(*dshape)) * scale_noise

        if addToCol: 
            data+=colData[row0:(row0+nr)]
            info(" $addToCol + noise --> $column (rows $row0 to %d)"%(row0+nr-1))
        else : info("Adding noise to $column (rows $row0 to %d)"%(row0+nr-1))

        tab.putcol(column, data, row0, nr)
    tab.close() 


def adaptFITS(imagename):
    """ Try to re-structre FITS file so that it conforms to lwimager standard """
    
    hdr = pyfits.open(imagename)[0].header
    naxis = hdr["NAXIS"]
    
    # Figure out if any axes have to be added before we proceed
    if naxis>=2 and naxis < 4:
        _freq = "--add-axis=freq:$FREQ0:DFREQ:Hz"
        _stokes = "--add-axis=stokes:1:1:1:Jy/Beam"
    
        if naxis == 2:
            info("FITS Image has 2 axes. Will add FREQ and STOKES axes. We need these predict visibilities")
            x.sh("fiitstool.py ${_stokes} ${_freq} $imagename")

        elif naxis==3:
            if hdr["CTYPE3"].lower().startswith("freq"):
                info("FITS Image missing FREQ axis. Adding it")
                # Will also need to reorder if freq is 3rd axis
                x.sh("fitstool.py ${_stokes} $imagename && fitstool.py --reorder=1,2,4,3 $imagename")

            elif hdr["CTYPE3"].lower().startswith("stokes"):
                info("FITS Image missing STOKES axis. Adding it")
                x.sh("fitstool.py ${_freq} $imagename")

    with pyfits.open(imagename) as hdu:
        hdr = hdu[0].header
        freq_ind = filter(lambda ind: hdr["CTYPE%d"%ind].startswith("FREQ"), range(1,5) )[0]

        if hdr["CDELT%d"%freq_ind] <0:
            dfreq = abs(hdr["CDELT%d"%freq_ind])
            nchan = hdr["NAXIS%d"%freq_ind]
            freq0 = hdr["CRVAL%d"%freq_ind]
            hdu[0].header["CDELT%d"%freq_ind] = dfreq
            hdu[0].header["CRVAL%d"%freq_ind] = freq0 - nchan*dfreq
            hdu.writeto(imagename, clobber=True)
        
    info("You image is now RATT approved ;) ")
