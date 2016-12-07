import inner_taper as taper
import os
import sys

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

msname = "%s/%s"%(MSDIR, jdict["msname"])
res = jdict["res"]
freq = jdict["freq"]
reset = jdict.get("reset", False)


savefig = "%s/%s_%.2f-%.2f.png"%(OUTPUT, jdict["msname"][:-3], res[0], res[1])

taper.taper(msname, res=res, freq=freq, savefig=savefig)

if reset:
    taper.reset(msname)
