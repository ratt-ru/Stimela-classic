import os
import sys
import json
import pyfits
import codecs

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
MAC_OS = os.environ["MAC_OS"]

if MAC_OS.lower() in ["yes", "true", "yebo", "1"]:
    MAC_OS = True
else:
    MAC_OS = False

outfile = "temp.json"

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

# possible combinations for specifying VLA configurations
VLA_CONFS = ["vla"]+["vla-%s"%s for s in "abcd"] + ["vla%s"%s for s in "abcd"] + ["jvla-%s"%s for s in "abcd"] + ["jvla%s"%s for s in "abcd"]
def which_vla(name):
    name = name.lower()
    if name in ["vla", "jvla"]:
        return "jvlad"
    elif name in VLA_CONFS:
        return "jvla%s"%(name[-1])
    else:
        raise NameError("Telescope name could not recognised")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    out = {}

    for key,val in jdict.iteritems():

        if isinstance(val, unicode):
            val = str(val)

        out[str(key)] = val

    return out


jdict = utils.readJson(CONFIG)
telescope = jdict["telescope"]
if telescope[:3] in ["vla", "jvl"] and jdict.get("antennas", None) in [None, False, ""]:
    telescope = which_vla(telescope)

direction = jdict.get("direction", None)


jdict["outdir"] = "." if MAC_OS else MSDIR
msname = jdict["msname"]

if jdict.get("antennas", False):
    jdict["pos"] = INDIR+"/"+jdict.get("antennas", "meetkat")
    jdict["coords"] = jdict.get("coord_sys", "enu")
else:
    jdict["pos"] = "/data/observatories/"+_ANTENNAS[telescope]
    if not os.path.isdir(jdict["pos"]):
        jdict["pos_type"] = "ascii"
        jdict["coords"] = "itrf"

jdict["tel"] = _OBS[telescope]

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
        naxis = hdr["naxis"]

        freq = filter(lambda ind: hdr["ctype%d"%ind].startswith("FREQ"),
                range(2, naxis+1, 1))
        if freq:
            freq = freq[0]
        else:
            raise TypeError("Your FITS image has no frequency information")

        nchan = hdr["naxis%d"%freq]
        freq0 = hdr["crval%d"%freq]
        dfreq = abs(hdr["cdelt%d"%freq])

        jdict["freq0"] = freq0
        jdict["dfreq"] = dfreq
        jdict["nchan"] = nchan

        if not direction:
            jdict["direction"] = "J2000,%fdeg,%fdeg"%(hdr["crval1"], hdr["crval2"])

with codecs.open(outfile, "w", "utf8") as std:
    std.write( json.dumps(jdict, ensure_ascii=False) )

# Run simms
utils.xrun("simms", ["-jc", outfile])

# move to
if MAC_OS:
    if os.path.exists("{:s}/{:s}".format(MSDIR, msname)):
        utils.xrun("rm", ["-fr", "{:s}/{:s}".format(MSDIR, msname)])
    utils.xrun("mv", [msname, MSDIR])
