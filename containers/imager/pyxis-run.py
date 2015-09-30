import Pyxis
import ms
import lsm
import im
from Pyxis.ModSupport import *
import os
import json


INDIR = os.environ["INDIR"]
v.OUTDIR = os.environ["OUTDIR"]
CONFIG = os.environ["CONFIG"]

LOG = II("${OUTDIR>/}log-imaging.txt"}


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = val

    return jdict


def azishe():

    jdict = readJson(CONDFIG)

    v.MS = "{:s}/{:s}".format(INDIR,jdict["msname"])

    im.cellsize = jdict.get("cellsize", "0.1arcsec")
    im.npix = jdict.get("npix", 8192)
    im.weight = jdict.get("weight", "briggs")
    im.robust = jdict.get("robust", 0)
    imagers = jdict.get("imagers", ["casa"])
    chanelise = jdict.get("channelise", 0)
    dirty = jdict.get("dirty", True)
    clean = jdict.get("clean", False)
    psf = jdict.get("psf", False)

    ms.set_default_spectral_info()

    casa_opts = dict(usescratch=True)
    wsclean_opts = dict(mgain=0.75)

    for imager in imagers:
        im.IMAGER = imager
        options = {}

        if imager == "casa":
            options = casa_opts
        elif imager== "wsclean":
            options = wsclean_opts

        im.make_image(dirty=dirty, restore=clean, 
                      restore_lsm=False, psf=False,
                      channelize=channelise, **options)
