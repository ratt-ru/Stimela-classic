import Pyxis
import ms
import im
import std
from Pyxis.ModSupport import *
import im.lwimager
import im.argo
import pyfits

import tempfile
import json
import numpy
import os

import pyrap.measures
dm = pyrap.measures.measures()

def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict

OUTDIR = os.environ["OUTPUT"]
INDIR = os.environ["INPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]
LOG_Template = "${OUTDIR>/}log-lwimager_predict.txt"
v.OUTFILE = II("${OUTDIR>/}results-${MS:BASE}")


def azishe():

    # Get parameters
    jdict = readJson(CONFIG)

    v.MS = "{:s}/{:s}".format(MSDIR, jdict.get("msname"))
    v.LOG_Template = "${OUTDIR>/}log-${MS:BASE}-lwimager_predict.txt"

    for item in [INDIR, "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = II("${lsmname:FILE}")
    
    std.copy(lsmname, LSM)

    adaptFITS(LSM)

    if jdict["recentre"]:
        direction = jdict["direction"].split(",")
        radec = dm.direction(*direction)

        with pyfits.open(LSM) as hdu:
            hdu[0].header["crval1"] = numpy.rad2deg( radec["m0"]["value"] )
            hdu[0].header["crval2"] = numpy.rad2deg( radec["m1"]["value"] )
            hdu.writeto(LSM, clobber=True)

    column = jdict.get("column", "DATA")
    if column not in ["DATA", "CORRECTED_DATA", "MODEL_DATA"]:
        im.argo.addcol(colname=column)

    add_to_col = jdict.get("add_to_column", None)
    copy = jdict.get("copy_to_CORRECTED_DATA", False)
    addnoise = jdict.get("addnoise", True)

    ms.set_default_spectral_info()


    if add_to_col:
        im.lwimager.predict_vis(image=LSM, padding=1.5, wprojplanes=128, column="MODEL_DATA")

        tab = ms.msw()
        data = tab.getcol("MODEL_DATA") + tab.getcol(add_to_col)
        tab.putcol(column, data)

        tab.close() 
    else:
        im.lwimager.predict_vis(image=LSM, padding=1.5, wprojplanes=128, column=column)


    if addnoise:
        sefd = jdict.get("sefd", 551) # default is MeerKAT L-Band
        noise = compute_vis_noise(sefd)
        simnoise(noise, addToCol=column, column=column)

    if copy and column!="CORRECTED_DATA":
        ms.copycol(fromcol=column, tocol="CORRECTED_DATA")


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
