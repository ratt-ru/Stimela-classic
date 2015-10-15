import os
import sys
import json
import pyfits
import codecs

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]

def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict

jdict = readJson(CONFIG)

if jdict.get("predict", False):
    imagename = "{:s}/skymodels/{:s}".format(INDIR, jdict["skymodel"])
    del jdict["skymodel"]
    del jdict["predict"]
else:
    sys.exit(0)

with pyfits.open(imagename) as hdu:
    hdr = hdu[0].header

    freq = filter(lambda ind: hdr["ctype%d"%ind].startswith("FREQ"),
            range(2, 5, 1))
    if freq:
        freq = freq[0]
    else:
        raise TypeError("Your FITS image has no frequency information")

    nchan = hdr["naxis%d"%freq]
    freq0 = hdr["crval%d"%freq]
    dfreq = hdr["cdelt%d"%freq]

    jdict["freq0"] = freq0
    jdict["dfreq"] = dfreq
    jdict["nchan"] = nchan

with codecs.open(CONFIG, "w", "utf8") as std:
    std.write( json.dumps(jdict, ensure_ascii=False) )

