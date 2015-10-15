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

LOG = II("${OUTDIR>/}log-meqtrees_sim.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict


def azishe():

    jdict = readJson(CONFIG)
    add = jdict.get("add_component_model", False)

    v.MS = "{:s}/{:s}".format(OUTDIR, jdict["msname"])

    lsmname = "{:s}/skymodels/{:s}".format(INDIR, jdict["skymodel"])
    v.LSM = II("${lsmname:FILE}")
    std.copy(lsmname, LSM)

    direction = jdict["direction"]

    if jdict["recentre"]:
        x.sh("tigger-convert --recenter=$direction $LSM -f")

    options = {}

    addnoise = jdict["addnoise"]
    if addnoise:
        sefd = jdict["sefd"]
        noise = compute_vis_noise(sefd)
        options["noise_stddev"] = noise

    mqt.msrun(II("${mqt.CATTERY}/Siamese/turbo-sim.py"), 
              job = '_tdl_job_1_simulate_MS', 
              section = "add" if add else "sim", 
              options = options,
              args = ["${ms.MS_TDL}", "${lsm.LSM_TDL}"])


def compute_vis_noise(sefd):
    """Computes nominal per-visibility noise"""

    tab = ms.ms()
    spwtab = ms.ms(subtable="SPECTRAL_WINDOW")

    freq0 = spwtab.getcol("CHAN_FREQ")[ms.SPWID, 0]
    wavelength = 300e+6/freq0
    bw = spwtab.getcol("CHAN_WIDTH")[ms.SPWID, 0]
    dt = tab.getcol("EXPOSURE", 0, 1)[0]
    dtf = (tab.getcol("TIME", tab.nrows()-1, 1)-tab.getcol("TIME", 0, 1))[0]

    # close tables properly, else the calls below will hang waiting for a lock...
    tab.close()
    spwtab.close()

    info(">>> $MS freq %.2f MHz (lambda=%.2fm), bandwidth %.2g kHz, %.2fs integrations, %.2fh synthesis"%(freq0*1e-6, wavelength, bw*1e-3, dt, dtf/3600))
    noise = sefd/math.sqrt(abs(2*bw*dt))
    info(">>> SEFD of %.2f Jy gives per-visibility noise of %.2f mJy"%(sefd, noise*1000))

    return noise 

