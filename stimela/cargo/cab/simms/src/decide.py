import os
import sys
import json
import pyfits
import codecs

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]

outfile = sys.argv[1]

_ANTENNAS = {
     "meerkat": "meerkat.itrf.txt",
     "kat-7": "kat-7.itrf.txt",
     "jvlaa": "vlaa.itrf.txt",
     "jvlab": "vlab.itrf.txt",
     "jvlac": "vlac.itrf.txt",
     "jvlad": "vlad.itrf.txt",
     "wsrt": "wsrt.itrf.txt",
     "ska1mid254": "skamid254.itrf.txt",
     "ska1mid197": "skamid197.itrf.txt",
}

_OBS = {
     "meerkat": "meerkat",
     "kat-7": "kat-7",
     "jvlaa": "vla",
     "jvlab": "vla",
     "jvlac": "vla",
     "jvlad": "vla",
     "wsrt": "wsrt",
     "ska1mid254": "meerkat",
     "ska1mid197": "meerkat",
}



def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    out = {}

    for key,val in jdict.iteritems():

        if isinstance(val, unicode):
            val = str(val)

        out[str(key)] = val

    return out


direction = jdict.get("direction", None)
jdict = readJson(CONFIG)
telescope = jdict["telescope"]

jdict["outdir"] = MSDIR
jdict["tel"] = _OBS[telescope]

if jdict.get("antennas", False):
    jdict["pos"] = INDIR+"/"+jdict.get("antennas", "meetkat")
    jdict["coords"] = jdict.get("coord_sys", "enu")
else:
    jdict["pos"] = "/data/observatories/"+_ANTENNAS[telescope]
    if not os.path.isdir(jdict["pos"]):
        jdict["pos_type"] = "ascii"
        jdict["coords"] = "itrf"

for item in ["antennas", "coord_sys", "telescope"]:
    jdict.pop(item, None)

imagename = jdict.pop("skymodel", False)

if jdict.pop("predict", False) and imagename:

    for item in [INDIR, "/data/skymodels"]:
        _imagename = "{:s}/{:s}".format(item, imagename)
        if os.path.exists(_imagename):
            break

    imagename = _imagename

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

        # get direction
        if not direction:
            ra0 = hdr["crval1"]
            dec0 = hdr["crval2"]

            jdict["direction"] = "J2000,%fdeg,%fdeg"%(ra0, dec0)
            raise SystemExit(direction)

with codecs.open(outfile, "w", "utf8") as std:
    std.write( json.dumps(jdict, ensure_ascii=False) )

raise SystemExit("adfhgsdjsadjfkhsd sdfkhgsdgfhsgf")
