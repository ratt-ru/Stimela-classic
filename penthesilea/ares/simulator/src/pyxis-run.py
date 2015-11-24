import Pyxis
import ms
import lsm
import mqt
import std
from Pyxis.ModSupport import *
import os
import json
import glob

def _loadconfs_Template():
    deps = glob.glob("/utils/utils/pyxis-*.py")
    for dep in deps:
        Pyxis.loadconf(dep)


mqt.MULTITHREAD = 16
INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]

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
    add = jdict.get("add_to_column", False)

    v.MS = "{:s}/{:s}".format(MSDIR, jdict["msname"])
    column = jdict.get("column", "DATA")

    if jdict["skymodel"] in [None, False]:
        sefd = jdict["sefd"]
        noise = compute_vis_noise(sefd)
        simnoise(noise, column=column)

        if column!="CORRECTED_DATA":
            ms.copycol(fromcol=column, tocol="CORRECTED_DATA")

        return

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


    mode = '"add to MS"' if add else '"sim only"'
    options["sim_mode"] = mode
    options["ms_sel.input_column"] = add
    options["ms_sel.output_column"] = column

    mqt.msrun(II("${mqt.CATTERY}/Siamese/turbo-sim.py"), 
              job = '_tdl_job_1_simulate_MS', 
              section = _section[section],
              options = options,
              args = ["${lsm.LSM_TDL}"])

    if column!="CORRECTED_DATA":
        ms.copycol(fromcol=column, tocol="CORRECTED_DATA")

