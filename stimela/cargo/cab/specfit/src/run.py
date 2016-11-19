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


lsmname = "%s/%s"%(INPUT,lsmname)

substitute = utils.substitute_globals

if spi_image:
    spi_image = substitute(spi_image) or "%s/%s"%(INPUT, spi_image)
    if spi_err:
        spi_err = substitute(spi_err) or "%s/%s"%(INPUT, spi_err)

    if make_spi:
        spi_image = spi_image + ".alpha.fits"
        spi_err = spi_image + ".alpha.err.fits"

made_spi = False

if image and make_spi:
    if isinstance(image, (str, unicode)):
        cube = substitute(image) or "%s/%s"%(INPUT,image)

    elif isinstance(image, (list, tuple)):
        for i,im in enumerate(image):
            image[i] = substitute(im) or "%s/%s"%(INPUT, im)
        cube = image
    else:
        raise TypeError("Image has to be either a string or list of strings")

    made_spi = True
    if mask:
            mask = substitute(mask) or "%s/%s"%(INPUT, mask)
    import specfit
    specfit.spifit(cube, mask=mask, sigma=sigma,
                  spi_image=spi_image,
                  spi_err_image=spi_err)


if add_spi and lsmname:
    print "Extracting spi from image"
#    if not made_spi:
#        spi_image = substitute(spi_image) or "%s/%s"%(INPUT, spi_image)

    if isinstance(freq0, (str, unicode)):
        freq0 = str(freq0)
        freq0 = substitute(freq0) or "%s/%s"%(INPUT,freq0)

    import addSPI
    addSPI.addSPI(spi_image, spi_err, lsmname, outlsm or lsmname, freq0=freq0, spitol=tol)

