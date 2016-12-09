import os
import sys
import re
import glob

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]


jdict = dict(npix=2048, wprojplanes=128, clean_iterations=1000, cellsize=2, 
             weight="briggs", robust=0, gridmode="widefield", spw=0, 
             field=0, stokes="I", aterm=False, psfmode="clark", 
             imagermode="csclean", keep_casa_images=False)

jdict.update( utils.readJson(CONFIG) )

jdict["cellsize"] = "%.4earcsec"%jdict["cellsize"]

STANDARD_OPTS = { 
    "field_id" : "field",
    "spw_id" : "spw",
    "imageprefix" : "imagename",
    "weight" : "weighting",
    "npix" : "imsize",
    "cellsize": "cell",
    "clean_iterations" : "niter",
}

options = {}

for key, value in jdict.items():
    key = STANDARD_OPTS.get(key, key)

    if value not in [None, []]:
        options[key] = value
    if key in options and options[key] == None:
        del options[key]

    if key in ["field", "spw"]:
        options[key] = str(options[key])
    if key in ["psf", "dirty"]:
        options.pop(key, None)


vis = options.pop("msname")
prefix = options["imagename"] = OUTPUT + "/" + options.pop("imagename", os.path.basename(vis[:-3]))
options["vis"] = MSDIR + "/" + vis

nterms = jdict.get("nterms", 0)
images = ["flux", "model", "residual", "psf", "image"]
STD_IMAGES = images[:4]

keep_casa_images = options["keep_casa_images"]
utils.icasa("clean", **options)

for image in images:
    img ="{:s}.{:s}".format(prefix, image)
    if nterms:
        _images = ["%s.tt%d"%(img,d) for d in range(nterms)]
        if image=="image":
            if  nterms==2:
                alpha = img+".alpha"
                alpha_err = img+".alpha.error"
                _images += [alpha,alpha_err]
            if  nterms==3:
                beta = img+".beta"
                beta_err = img+".beta.error"
                _images += [beta,beta_err]
    else:
        _images = [img]

    for _image in  _images:
        if _image is STD_IMAGES and (not os.path.exists(_image)):
            raise RuntimeError("Standard output from CASA clean task not found. Something went wrong durring cleaning, take a look at the logs and such")
        elif os.path.exists(_image):
            utils.icasa("exportfits", imagename=_image, fitsimage=_image+".fits")

        if not keep_casa_images:
            utils.xrun("rm", ["-rf", img])
