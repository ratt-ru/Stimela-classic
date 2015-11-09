import Pyxis
import ms
import lsm
import mqt
import std
from Pyxis.ModSupport import *
import os
import json


mqt.MULTITHREAD = 16
INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]

LOG = II("${OUTDIR>/}log-subtract.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict


def azishe():

    jdict = readJson(CONFIG)

    v.MS = "{:s}/{:s}".format("/msdir", jdict["msname"])

    for item in ["/input/", "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = lsmname

    options = {}

    fromcol = jdict.get("fromcol", "DATA")
    tocol = jdict.get("tocol", "CORRECTED_DATA")

    options["ms_sel.input_column"] = fromcol
    options["ms_sel.output_column"] = tocol
    subset = jdict.get("subset", False)
    if subset:
        options["tiggerlsm.lsm_subset"] = subset

    mqt.msrun(II("${mqt.CATTERY}/Siamese/turbo-sim.py"), 
              job = '_tdl_job_1_simulate_MS', 
              section = "subtract",
              options = options,
              args = ["${lsm.LSM_TDL}"])
