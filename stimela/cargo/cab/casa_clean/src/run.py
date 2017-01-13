from __future__ import print_function
import os
import sys

import drivecasa
casa = drivecasa.Casapy()

sys.path.append('/utils')
import utils

CONFIG = os.environ['CONFIG']
cab = utils.readJson(CONFIG)

params = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    params[name] = value

port2fits = params.pop('port2fits', True)
keep_casa_images = params.pop("keep_casa_images", False)
script = ['clean(**{})'.format(params)]

nterms = params.get("nterms", 1)
images = ["flux", "model", "residual", "psf", "image"]
STD_IMAGES = images[:4]

prefix = params['imagename']
convert = []
if port2fits:
    for image in images:
        img ="{:s}.{:s}".format(prefix, image)
        if image == 'flux':
            _images = [img]
        elif nterms>1:
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
        convert += _images

for _image in  convert:
    sys.stdout.write(_image)
    if _image in STD_IMAGES and (not os.path.exists(_image)):
        raise RuntimeError("Standard output from CASA clean task not found. Something went wrong durring cleaning, take a look at the logs and such")

    elif os.path.exists(_image):
        script += ['exportfits(**{})'.format( dict(imagename=_image, fitsimage=_image+".fits"))]

out = casa.run_script(script, raise_on_severe=False)

if not keep_casa_images:
    for _image in convert:
        utils.xrun("rm", ["-rf", _image])
