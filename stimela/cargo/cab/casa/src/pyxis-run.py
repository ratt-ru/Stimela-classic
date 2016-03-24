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
else:
    MAC_OS = False

output = "./temp-output-tmp"
v.OUTDIR = output if MAC_OS else os.environ["OUTPUT"]
outdir = os.environ["OUTPUT"]

v.DESTDIR = "."

OUTFILE_Template = "${OUTDIR>/}results-${MS:BASE}"

LOG = II("${OUTDIR>/}log-casa.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict


def azishe():

    jdict = readJson(CONFIG)

    v.MS = "{:s}/{:s}".format(MSDIR, jdict["msname"])
    prefix = jdict.get("imageprefix", MS.split("/")[-1][:-3])
    v.LOG = II("${OUTDIR>/}log-${prefix}-casa.txt")
    prefix = OUTDIR +"/"+ prefix

    im.cellsize = "{:f}arcsec".format( jdict.get("cellsize", 1) )
    im.npix = jdict.get("npix", 4096)
    im.weight = jdict.get("weight", "briggs")
    im.robust = jdict.get("robust", 0)
    im.stokes = jdict.get("stokes", "I")
    channelise = jdict.get("channelise", 0)
    dirty = jdict.get("dirty", True)
    niter = jdict.get("clean_iterations", 0)

    if niter>0:
        im.niter = niter
        clean = True
    else:
        clean = False

    psf = jdict.get("psf", False)

    im.DIRTY_IMAGE = prefix + ".dirty.fits"
    im.MODEL_IMAGE = prefix + ".model.fits"
    im.RESIDUAL_IMAGE = prefix + ".residual.fits"
    im.RESTORED_IMAGE = prefix + ".restored.fits"
    im.FULLREST_IMAGE = prefix + ".fullrest.fits"
    im.PSF_IMAGE = prefix + ".psf.fits"

    ms.set_default_spectral_info()

    casa_opts = dict(usescratch=True)
    wsclean_opts = dict(mgain=0.75)

    im.IMAGER = "casa"


    im.make_image(dirty=dirty, restore=clean, 
                  restore_lsm=False, psf=psf,
                  channelize=channelise,
                  usescratch=True)

    if MAC_OS:
        x.sh("mv $output/* $outdir")
