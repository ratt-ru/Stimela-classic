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

    v.MS = "/msdir/{:s}".format(jdict["msname"])

    for item in ["/input/", "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = II("${lsmname:FILE}")
    std.copy(lsmname, LSM)

    direction = jdict["direction"]

    if jdict["recentre"]:
        x.sh("tigger-convert --recenter=$direction $LSM -f")

    options = {}

    addnoise = False if add else jdict["addnoise"]
    if addnoise:
        sefd = jdict["sefd"]
        noise = compute_vis_noise(sefd)
        options["noise_stddev"] = noise

    beam = jdict["E_jones"]
    if beam:
        options["me.e_enable"] = 1
        options["me.p_enable"] = 1

        if jdict["beam_file_type"] == "fits":
            options["pybeams_fits.filename_pattern"] = "/data/beams/" + jdict["beam_files_pattern"]
            options["me.e_module"] = "Siamese_OMS_pybeams_fits"
        elif jdict["beam_file_type"] == "emss":
            options["me.e_module"] = "Siamese_OMS_emss_beams_emss_polar_beams"
            options["emss_polar_beams.filename_pattern"] = "/data/beams/" + jdict["beam_files_pattern"]
            options["emss_polar_beams.pattern_labels"] = jdict["emss_labels"]
            options["emss_polar_beams.freq_labels"] = jdict["emss_freqs"]

    _section = dict(sim = "sim",
                    add_G = "sim:G")
    #TODO(sphe) Add E-Jones option

    if jdict.get("G_Jones", False):
        section = "add_G"
    else:
        section = "sim"

    column = jdict.get("column", "DATA")

    mode = "add to MS" if add else "sim only"
    options["sim_mode"] = mode
    options["ms_sel.input_column"] = column
    options["ms_sel.output_column"] = column

    mqt.msrun(II("${mqt.CATTERY}/Siamese/turbo-sim.py"), 
              job = '_tdl_job_1_simulate_MS', 
              section = _section[section],
              options = options,
              args = ["${lsm.LSM_TDL}"])

    if column!="CORRECTED_DATA":
        ms.copycol(fromcol=column, tocol="CORRECTED_DATA")


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
