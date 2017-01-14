import os
import sys
import json
import pyfits
import codecs
import subprocess
from lofar import bdsm
import Tigger
import copy
import numpy
from astLib.astWCS import WCS

from Tigger.Models import SkyModel, ModelClasses

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
OUTDIR = os.environ["OUTPUT"]

jdict = utils.readJson(CONFIG)
template = utils.readJson("/code/sourcery_template.json")


name = jdict.pop("imagename")
dimage = jdict.pop("detection_image", None)
psf = jdict.pop("psf", None)
prefix = jdict.pop("prefix", None) or name.split("/")[-1]

for item in "name psf dimage prefix".split():
    if isinstance(globals()[item], str):
        tmp = OUTDIR + "/" + globals()[item]  if item=="prefix" else INDIR + "/" + globals()[item]
        globals()[item] = utils.substitute_globals(globals()[item]) or tmp


def pybdsm(image, prefix, *args, **kw):
    img = bdsm.process_image(image, *args, **kw)
    gaulfile = prefix+".gaul.fits"
    img.write_catalog(catalog_type="gaul", format="fits", outfile=gaulfile, clobber=True)

    # convert to Gaul file to Tigger LSM
    # First make dummy tigger model
    tname = prefix.split("/")[-1] + ".txt"
    tname_lsm = prefix + ".lsm.html"
    with open(tname, "w") as stdw:
        stdw.write("#format:name ra_d dec_d i emaj_s emin_s pa_d\n")

    model = Tigger.load(tname)

    def tigger_src(gaul, idx):

        name = "SRC%d"%idx

        flux = ModelClasses.Polarization(gaul["Total_flux"], 0, 0, 0, I_err=gaul["E_Total_flux"])

        ra, ra_err = map(numpy.deg2rad, (gaul["RA"], gaul["E_RA"]) )
        dec, dec_err = map(numpy.deg2rad, (gaul["DEC"], gaul["E_DEC"]) )
        pos =  ModelClasses.Position(ra, dec, ra_err=ra_err, dec_err=dec_err)

        ex, ex_err = map(numpy.deg2rad, (gaul["DC_Maj"], gaul["E_DC_Maj"]) )
        ey, ey_err = map(numpy.deg2rad, (gaul["DC_Min"], gaul["E_DC_Min"]) )
        pa, pa_err = map(numpy.deg2rad, (gaul["PA"], gaul["E_PA"]) )

        if ex and ey:
            shape = ModelClasses.Gaussian(ex, ey, pa, ex_err=ex_err, ey_err=ey_err, pa_err=pa_err)
        else:
            shape = None
      
        return SkyModel.Source(name, pos, flux, shape=shape)

        
    with pyfits.open(gaulfile) as hdu:
        data = hdu[1].data

        for i, gaul in enumerate(data):
            model.sources.append(tigger_src(gaul, i))

    wcs = WCS(image)
    centre = wcs.getCentreWCSCoords()
    model.ra0, model.dec0 = map(numpy.deg2rad, centre)

    model.save(tname_lsm)
    # Rename using CORPAT
    utils.xrun("tigger-convert", [tname_lsm, "--rename -f"])




go = jdict.pop("pybdsm", False)

if go:
    if dimage:
        jdict["detection_image"] = dimage
    pybdsm(name, prefix, **jdict)
    sys.exit(0)

template["prefix"] = prefix
template["imagename"] = name

template["psfname"] = psf
template["reliability"]["thresh_pix"] = jdict.pop("thresh_pix", 4)
template["reliability"]["thresh_isl"] = jdict.pop("thresh_isl", 3)
if dimage:
    template["reliability"]["detection_image"] = dimage


# The tagging requires too much fine tunning. Turning it off by default
template["dd_tagging"]["enable"] = jdict.pop("dd_tagging", False)



for key in jdict:
    if key in template["reliability"].keys():
        template["reliability"][key] = jdict[key]
    elif key in template["dd_tagging"].keys():
        template["dd_tagging"][key] = jdict[key]


config = "run_me_now.json"
utils.writeJson(config, template)

utils.xrun("sourcery", ["-jc", config])
utils.xrun("tigger-convert", ["%s/%s.lsm.html"%(OUTDIR,prefix), "--rename -f"])

utils.xrun("rm", ["-f", config])
