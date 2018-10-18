import os
import sys
import re
import pyfits
from pyrap.tables import table

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)
params = {}
for param in cab['parameters']:
    params[param['name']] = param['value']

image = params.pop("image", None)
mask = params.pop("mask-image", None)
in_spi_image = params.pop("input-spi-image", None)
in_spi_err = params.pop("input-spi-error-image", None)
out_spi_image = params.pop("output-spi-image", None)
out_spi_err = params.pop("output-spi-error-image", None)
lsmname = params.pop("input-skymodel", None)
outlsm = params.pop("output-skymodel", None)
sigma = params.pop("sigma-level", 20) or 20
freq0 = params.pop("freq0", 0)
tol = params.pop("tolerance-range", None) or (-10,10)

if out_spi_image:
    import specfit
    specfit.spifit(image, mask=mask, sigma=sigma,
                  spi_image=out_spi_image,
                  spi_err_image=out_spi_err)
    spi_image = out_spi_image
    spi_err = out_spi_err
else:
    spi_image = in_spi_image
    spi_err = in_spi_err

if lsmname and outlsm:
    sys.stdout.write("Extracting spi from image")

    with pyfits.open(image) as hdu:
        header = hdu[0].header
        bmin = header['BMIN']
        bmaj = header['BMAJ']
        bpa = header['BPA']
    beam = (bmin, bmaj, bpa)

    import addSPI
    addSPI.addSPI(spi_image, spi_err, lsmname=lsmname, outfile=outlsm,
                  beam=beam, freq0=freq0, spitol=tol)
