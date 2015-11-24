import Pyxis
import ms
import lsm
import mqt
import std
import stefcal
from Pyxis.ModSupport import *
import os
import json


mqt.MULTITHREAD = 16
INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]

LOG = II("${OUTDIR>/}log-calibrator.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict


def azishe():

    jdict = readJson(CONFIG)
    prefix = jdict.get("prefix", None)

    v.MS = "{:s}/{:s}".format(MSDIR, jdict["msname"])

    for item in [INDIR, "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = lsmname

    column = jdict.get("column", "DATA")

    options = {}
    options["ms_sel.input_column"] = column

    stefcal.stefcal(section="stefcal", gain_plot_prefix=prefix,
                    reset=True, dirty=False, 
                    options= options)
