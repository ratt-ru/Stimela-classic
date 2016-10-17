import Pyxis
import ms
import lsm
import mqt
import std
from Pyxis.ModSupport import *
import os
import json
import glob
import numpy

def _loadconfs_Template():
    deps = glob.glob("/utils/utils/pyxis-*.py")
    for dep in deps:
        Pyxis.loadconf(dep)


mqt.MULTITHREAD = 16
INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]

v.LOG = II("${OUTDIR>/}log-simulation.txt")


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



    addnoise = jdict.get("addnoise", False)
    sefd = jdict.get("sefd", 500)

    v.MS = "{:s}/{:s}".format(MSDIR, jdict["msname"])
    
    v.LOG = II("${OUTDIR>/}log-${MS:BASE}-simulation.txt")

    column = jdict.get("column", "DATA")
    copy = jdict.get("copy_to_CORRECTED_DATA", False)

    newcol = jdict.get("custom_data_column", None)
    if newcol:
        im.argo.addcol(newcol)

    if jdict["skymodel"] in [None, False] and addnoise:
        noise = compute_vis_noise(sefd)
        simnoise(noise, column=column)

        if copy and column!="CORRECTED_DATA":
            ms.copycol(fromcol=column, tocol="CORRECTED_DATA")

        return

    for item in ["/input/", "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = II("${lsmname:FILE}")
    std.copy(lsmname, LSM)


    if jdict.get("recenter", False):
        direction = jdict.get("direction", False)
        if direction:
            ftab = ms.ms(subtable="FIELD")
            ra,dec = ftab.getcol("PHASE_DIR")[jdict.get("field_id",0)][0]

            direction = "J2000,%frad,%frad"%(ra,dec)

        x.sh("tigger-convert --recenter=$direction $LSM -f")

    options = {}

    if addnoise:
        noise = compute_vis_noise(sefd)
        options["noise_stddev"] = noise

    beam = jdict.get("Ejones", False)
    if beam:
        options["me.e_enable"] = 1
        options["me.p_enable"] = 1
        options["me.e_module"] = "Siamese_OMS_pybeams_fits"
        options["me.e_advanced"] = 1 
        options["me.e_all_stations"] = 1
        options["pybeams_fits.l_axis"] = jdict.get("beam_l_axis", "L")
        options["pybeams_fits.m_axis"] = jdict.get("beam_m_axis", "M")
        options["pybeams_fits.filename_pattern"] =  "%s/%s"%(INDIR, jdict["beam_files_pattern"])


        rms_perr = jdict.get("pointing_accuracy", 0)
        # Include pointing errors if needed
        if rms_perr:
            anttab = ms.ms(subtable="ANTENNA")
            NANT = anttab.nrows()

            options["me.epe_enable"] = 1
            perr = numpy.random.randn(NANT)*rms_perr, numpy.random.randn(NANT)*rms_perr
            ll, mm = " ".join( map(str, perr[0]) ), " ".join( map(str, perr[-1]) )
            options['oms_pointing_errors.pe_l.values_str'] = "'%s'"%ll
            options['oms_pointing_errors.pe_m.values_str'] = "'%s'"%mm


    _section = dict(sim = "sim",
                    add_G = "sim:G")
    if jdict.get("gjones", False):
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

    if copy and column!="CORRECTED_DATA":
        ms.copycol(fromcol=column, tocol="CORRECTED_DATA")

