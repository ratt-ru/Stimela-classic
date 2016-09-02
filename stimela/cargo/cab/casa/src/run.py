import os
import sys
import re

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

images = ["flux", "model", "residual", "psf", "image", "tt0", "alpha", "alpha.error", "beta", "beta.error"]
STD_IMAGES = images[:4]

keep_casa_images = options["keep_casa_images"]
utils.icasa("clean", **options)

for image in images[:5]:
    img ="{:s}.{:s}".format(prefix, image)
    fits = img + ".fits" if image!="image" else img.replace(".image", ".restored.fits")

    if image is STD_IMAGES and (not os.path.exists(img)):
        raise RuntimeError("Standard output from CASA clean task not found. Something went wrong durring cleaning, take a look at the logs and such")

    elif os.path.exists(img):
        utils.icasa("exportfits", imagename=img, fitsimage=fits)

        if not keep_casa_images:
            utils.xrun("rm", ["-rf", img])
