import os
import sys
import pyfits

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

params = cab["parameters"]

_positional = ['antenna-file']
positional = []
for item in _positional:
    param = filter( lambda a: a['name']==item, params)[0]
    if param['value']:
        positional.append(param['value'])

#f params.pop("from-fits", False) and imagename:
#   with pyfits.open(imagename) as hdu:
#       hdr = hdu[0].header
#       naxis = hdr["naxis"]

#       freq = filter(lambda ind: hdr["ctype%d"%ind].startswith("FREQ"),
#               range(2, naxis+1, 1))
#       if freq:
#           freq = freq[0]
#       else:
#           raise TypeError("Your FITS image has no frequency information")

#       nchan = hdr["naxis%d"%freq]
#       freq0 = hdr["crval%d"%freq]
#       dfreq = abs(hdr["cdelt%d"%freq])

#       params["freq0"] = freq0
#       params["dfreq"] = dfreq
#       params["nchan"] = nchan

#       if not direction:
#           params["direction"] = "J2000,%fdeg,%fdeg"%(hdr["crval1"], hdr["crval2"])

args = []
for param in params:
    key = param['name']
    value = param['value']
    if value in [None, False]:
        continue
    if value is True:
        arg = '{0}{1}'.format(cab['prefix'], key)
    elif hasattr(value, '__iter__'):
        arg = ' '.join(['{0}{1} {2}'.format(cab['prefix'], key, val) for val in value])
    else:
        if isinstance(value, str):
            value = '"{}"'.format(value)
        arg = '{0}{1} {2}'.format(cab['prefix'], key, value)

    args.append(arg)

utils.xrun(cab['binary'], args+['--nolog']+positional)
