import os
import sys
import re

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]


jdict = dict(npix=2048, clean_iterations=1000, cellsize=2, 
             weight="briggs", robust=0, spw_id=0, 
             field_id=0, stokes="I", mgain=0.85, column="CORRECTED_DATA")

jdict.update( utils.readJson(CONFIG) )

jdict["cellsize"] = jdict["cellsize"]/3600.0

weight = jdict.get("weight")
if weight=="briggs":
    jdict["weight"] = "%s %f"%(weight, jdict.pop("robust", 0))
else:
    jdict.pop("robust", None)


STANDARD_OPTS = { 
    "field_id" : "field",
    "spw_id" : "spw",
    "imageprefix" : "name",
    "npix" : "size",
    "cellsize": "scale",
    "clean_iterations" : "niter",
    "stokes" : "pol",
    "column" : "datacolumn",
}

options = {}

jdict.pop("spw_id", None)
jdict.pop("spw", None)
jdict.pop("imager", None)

for key, value in jdict.items():
    key = STANDARD_OPTS.get(key, key)

    if value not in [None, []]:
        options[key] = value
    if key in options and options[key] == None:
        del options[key]
    if value == False:
        del options[key]
    elif value == True:
        options[key] = ""

    if key in ["field", "spw"]:
        options[key] = str(options.get("field", 0))
    if key in ["psf", "dirty"]:
        options.pop(key, None)

options["size"] = "%d %d"%(options["size"], options["size"])

msname = options.pop("msname")

if isinstance(msname, (list, tuple)):
    mslist = " ".join(["%s/%s"%(MSDIR, ms) for ms in msname])
    vis = msname[0]
else:
    vis = msname
    mslist = MSDIR + "/" + msname
prefix = options["name"] = OUTPUT + "/" + options.pop("name", os.path.basename(vis[:-3]))

args = ["-%s %s"%(a,b) for a,b in options.iteritems()]
print args

utils.xrun("wsclean", args + [mslist])
