import os
import sys
import re
import pyfits

sys.path.append('/scratch/stimela')
import utils

CONFIG = os.environ['CONFIG']
INPUT = os.environ['INPUT']
OUTPUT = os.environ['OUTPUT']
MSDIR = os.environ['MSDIR']

cab = utils.readJson(CONFIG)
params = cab['parameters']
args = []

# new interface as of WSCLEAN v2.5
# make the transition transparent

npix = filter(lambda x: x['name'] == 'size', params)[0]['value']

if isinstance(npix, int):
    npix = [npix, npix]
elif isinstance(npix, list) and len(npix) == 1:
    npix = npix * 2
elif not (isinstance(npix, list) and
          all([isinstance(px, int) for px in npix]) and
          len(npix) == 2) :
    raise ValueError("Npix only accepts single int or list[2] of int")

trdefault = int(max(npix[0], npix[1]) * 0.75)
trim = filter(lambda x: x['name'] == 'trim', params)[0]['value']

if trim is None:
    trim = [trdefault, trdefault]
elif isinstance(trim, int):
    trim = [trim, trim]
elif isinstance(trim, list) and len(trim) == 1:
    trim = trim * 2
elif not (isinstance(trim, list) and
          all([isinstance(t, int) for t in trim]) and
          len(npix) == 2) :
    raise ValueError("trim only accepts single int or list[2] of int")
pad = max(npix[0], npix[1]) / float(min(trim[0], trim[1]))
trindex = filter(lambda x: x['name'] == 'trim', params)[0]
params.remove(trindex)
padding = filter(lambda x: x['name'] == 'padding', params)
if not padding:
    filter(lambda x: x['name'] == 'size', params)[0]["value"] = trim  # npix is now the unpadded size
    params.append({'name': 'padding', 'value': pad})  # replace with 'padding' argument

for param in params:
    name = param['name']
    value = param['value']

    if name == 'msname':
        if isinstance(value, str):
            mslist = value
        else:
            mslist = ' '.join(value)
        continue

    if value in [None, False]:
        continue
    # only versions > 2.0 have this 
    if name in ["spws"]:
        continue

    if name == 'scale':
        if isinstance(value, (int, float)):
            value = '{0}asec'.format(value)

    if name == 'datacolumn':
        name = 'data-column' # new interface as of WSCLEAN 2.5 - here for compat

    if name in 'size trim nwlayers-for-size beam-shape channel-range interval'.split():
        if isinstance(value, int):
            value = '{0} {0}'.format(value)
        elif hasattr(value, '__iter__'):
            if len(value) == 1:
                value.append( value[0])
            value = ' '.join(map(str, value))

    if name in 'spws multiscale-scales pol'.split():
        if hasattr(value, '__iter__'):
            value = ','.join(map(str, value))

    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], name)
    else:
        arg = '{0}{1} {2}'.format(cab['prefix'], name, value)

    args.append(arg)

if '{0}auto-threshold'.format(cab['prefix']) not in args:
    removed = False
    for item1 in args:
        if 'noise-image' in item1:
            noise_image = item1.split('{0}noise-image '.format(cab['prefix']))[-1]
            args.remove('{0}noise-image {1}'.format(cab['prefix'], noise_image))
            noise_hdu = pyfits.open(noise_image)
            noise_data = noise_hdu[0].data
            noise_std = noise_data.std()
            noise_hdu.close()
            for item2 in args:
                if 'noise-sigma' in item2:
                    noise_sigma = item2.split('{0}noise-sigma '.format(cab['prefix']))[-1]
                    args.remove('{0}noise-sigma {1}'.format(cab['prefix'], noise_sigma))
                    removed = True
                    threshold = float(noise_sigma)*noise_std
                    for item3 in args:
                        if '{0}threshold'.format(cab['prefix']) in item3:
                            args.remove(item3)
                    args.append('{0}threshold {1}'.format(cab['prefix'], threshold))
    if not removed:
        args.remove('{0}noise-sigma 3.0'.format(cab['prefix']))
else:
    args.remove('{0}noise-sigma 3.0'.format(cab['prefix']))

utils.xrun(cab['binary'], args + [mslist])
