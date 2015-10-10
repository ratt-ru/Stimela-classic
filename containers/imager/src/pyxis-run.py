import Pyxis
import ms
import lsm
import im
from Pyxis.ModSupport import *
import os
import json


INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]

LOG = II("${OUTDIR>/}log-imaging.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = val

    return jdict


def azishe():

    jdict = readJson(CONFIG)

    v.MS = "{:s}/{:s}".format(OUTDIR, jdict["msname"])

    im.cellsize = "{:f}arcsec".format( jdict.get("cellsize", 1) )
    im.npix = jdict.get("npix", 4096)
    im.weight = jdict.get("weight", "briggs")
    im.robust = jdict.get("robust", 0)
    imagers = jdict.get("imagers", ["wsclean"])
    channelise = jdict.get("channelise", 0)
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
