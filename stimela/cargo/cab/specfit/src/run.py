import os
import sys
import re
from pyrap.tables import table

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

image = jdict.pop("image", None)
mask = jdict.pop("mask", None)
make_spi = jdict.pop("make_spi", False)
spi_image = jdict.pop("spi_image", None)
spi_err = jdict.pop("spi_err_image", None)
lsmname = jdict.pop("skymodel", None)
outlsm = jdict.pop("skymodel_out", None)
sigma = jdict.pop("sigma", 20)
add_spi = jdict.pop("add_spi", None)
freq0 = jdict.pop("freq0", 0)
tol = jdict.pop("tol", None)


for item in "image mask spi_image spi_err lsmname outlsm freq0 lsmname".split():
    if isinstance(globals()[item], str):
    globals()[item] = utils.substitute_globals(globals()[item]) or INPUT + "/" + globals()[item]

if spi_image:
    if make_spi:
        spi_image = spi_image + ".alpha.fits"
        spi_err = spi_image + ".alpha.err.fits"

made_spi = False

if image and make_spi:
    if isinstance(image, (str, unicode)):
        cube = image

    elif isinstance(image, (list, tuple)):
        for i, im in enumerate(image):
            image[i] = im
        cube = image
    else:
        raise TypeError("Image has to be either a string or list of strings")

    made_spi = True
    import specfit
    specfit.spifit(cube, mask=mask, sigma=sigma,
                  spi_image=spi_image,
                  spi_err_image=spi_err)


if add_spi and lsmname:
    print "Extracting spi from image"

    if isinstance(freq0, (str, unicode)):
        freq0 = str(freq0)

    print "FREQ0", freq0
    sys.exit(0)
    import addSPI
    addSPI.addSPI(spi_image, spi_err, lsmname, outlsm or lsmname, freq0=freq0, spitol=tol)
