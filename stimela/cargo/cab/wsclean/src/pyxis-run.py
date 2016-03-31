import Pyxis
import ms
import im
from Pyxis.ModSupport import *
import os
import json


INDIR = os.environ["INPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]
MAC_OS = os.environ["MAC_OS"]

if MAC_OS.lower() in ["yes", "true", "yebo", "1"]:
    MAC_OS = True
    x.sh("mkdir msdir-tmp && cp -r $MSDIR /msdir-tmp")
    x.sh("mkdir input-tmp && cp -r $MSDIR /input-tmp")
    v.MSDIR = "/msdir-tmp"
    v.INPUT = "/input-tmp"
else:
    MAC_OS = False

output = "./temp-output"
v.OUTDIR = output if MAC_OS else os.environ["OUTPUT"]
outdir = os.environ["OUTPUT"]

v.DESTDIR = "."

OUTFILE_Template = "${OUTDIR>/}results-${MS:BASE}"

LOG = II("${OUTDIR>/}log-wsclean.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict


def azishe():

    jdict = readJson(CONFIG)

    v.MS = "%s/%s"%(MSDIR, jdict["msname"])

    prefix = jdict.pop("imageprefix", None) or II("${MS:BASE}")
    v.LOG = II("${OUTDIR>/}log-${prefix}-wsclean.txt")
    prefix = OUTDIR +"/"+ prefix

    im.cellsize = "{:f}arcsec".format( jdict.get("cellsize", 1) )
    im.npix = jdict.get("npix", 4096)
    im.weight = jdict.get("weight", "briggs")
    im.robust = jdict.get("robust", 0)
    im.stokes = jdict.get("stokes", "I")
    channelise = jdict.get("channelize", 0)
    column = jdict.get("column", "CORRECTED_DATA")
    dirty = jdict.get("dirty", True)
    niter = jdict.get("clean_iterations", 0)

    if niter>0:
        im.niter = niter
        clean = True
    else:
        clean = False
        dirty = True

    psf = jdict.get("psf", False)

    im.DIRTY_IMAGE = prefix + ".dirty.fits"
    im.MODEL_IMAGE = prefix + ".model.fits"
    im.RESIDUAL_IMAGE = prefix + ".residual.fits"
    im.RESTORED_IMAGE = prefix + ".restored.fits"
    im.FULLREST_IMAGE = prefix + ".fullrest.fits"
    im.PSF_IMAGE = prefix + ".psf.fits"

    ms.set_default_spectral_info()


    im.IMAGER = "wsclean"

    im.make_image(dirty=dirty, restore=clean, 
                  restore_lsm=False, psf=psf,
                  channelize=channelise,
                  mgain=0.75, column=column)

    x.sh("rm -f ${im.BASENAME_IMAGE}-first-residual.fits")

    if MAC_OS:
        x.sh("mv $output/* $outdir")
