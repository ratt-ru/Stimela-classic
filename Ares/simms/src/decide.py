import os
import sys
import json
import pyfits
import codecs

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]

_ANTENNAS = {
     "meerkat": "MeerKAT64_ANTENNAS",
     "kat-7": "KAT7_ANTENNAS",
     "jvlaa": "vlaa.itrf.txt",
     "jvlab": "vlab.itrf.txt",
     "jvlac": "vlac.itrf.txt",
     "jvlad": "vlad.itrf.txt",
     "wsrt": "WSRT_ANTENNAS",
     "ska1mid254": "SKA1REF2_ANTENNAS",
     "ska1mid197": "SKA197_ANTENNAS",
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

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict

jdict = readJson(CONFIG)
telescope = jdict.pop("telescope")
jdict["outdir"] = "/msdir"
jdict["tel"] = _OBS[telescope]

if jdict.get("antennas", False):
    jdict["pos"] = "/input/"+jdict.get("antennas", "meetkat")
    jdict["coords"] = jdict.get("coord_sys", "enu")
else:
    jdict["pos"] = "/data/observatories/"+_ANTENNAS[telescope]
    if not os.path.isdir(jdict["pos"]):
        jdict["pos_type"] = "ascii"
        jdict["coords"] = "itrf"

for item in ["antennas", "coord_sys"]:
    jdict.pop(item, None)

imagename = jdict.pop("skymodel", False)

if jdict.pop("predict", False) and imagename:

    for item in ["/input", "/data/skymodels"]:
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

with codecs.open(CONFIG, "w", "utf8") as std:
    std.write( json.dumps(jdict, ensure_ascii=False) )
