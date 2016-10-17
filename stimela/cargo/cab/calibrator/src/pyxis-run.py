import Pyxis
import ms
import lsm
import mqt
import std
import stefcal
from Pyxis.ModSupport import *
import os
import json


mqt.MULTITHREAD = 4
INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]

LOG = II("${OUTDIR>/}log-calibrator.txt")

MULTI = False


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict



def calibrate(jdict, multi=MULTI):

    v.MS = "%s/%s"%(MSDIR, ITER[0])
    skymodel = ITER[1]
    
    prefix = jdict.get("prefix", None)
    if prefix and not multi:
        v.LOG = II("${OUTDIR>/}log-${prefix}.txt")
    else:
        v.LOG = II("${OUTDIR>/}log-${MS:BASE}-calibration.txt")

    x.sh("addbitflagcol $MS")

    ms.set_default_spectral_info()


    for item in [INDIR, "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, skymodel)
        if os.path.exists(lsmname):
            break

    v.LSM = lsmname
    if jdict.get("label", ""):
        v.LABEL = jdict["label"]

    column = jdict.get("column", "DATA")

    ms.DDID = jdict.get("spw_id", 0)
    ms.FIELD = jdict.get("field_id", 0)

    options = {}
    kw = {}
    options["tiggerlsm.lsm_subset"] = jdict.get("subset", "all")
    gtimeint, gfreqint = jdict.get("Gjones_intervals", (1,1))

    options["stefcal_gain.timeint"] = gtimeint
    options["stefcal_gain.freqint"] = gfreqint
    options["stefcal_gain.flag_ampl"] = jdict.get("gjones_ampl_clipping", 0)
    options["stefcal_gain.flag_chisq"] = jdict.get("gjones_chisq_clipping", 0)
    options["stefcal_gain.flag_chisq_threshold"] = jdict.get("Gjones_thresh_sigma", 10)
    options["stefcal_gain.flag_ampl_low"] = jdict.get("Gjones_flag_ampl_low", 0.3)
    options["stefcal_gain.flag_ampl_high"] = jdict.get("Gjones_flag_ampl_high", 2)

    stefcal.STEFCAL_DIFFGAIN_INTERVALS = jdict.get("DDjones_intervals", None)
    stefcal.STEFCAL_DIFFGAIN_SMOOTHING = jdict.get("DDjones_smoothing", None)
    stefcal.STEFCAL_GAIN_SMOOTHING = jdict.get("Gjones_smoothing", None)

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

    options["ms_sel.input_column"] = column

    DDjones = jdict.get("DDjones", False)
    if DDjones:
        options["stefcal_diffgain.flag_ampl"] = 0
        options["stefcal_diffgain.flag_chisq"] = 0

    if jdict.get("IFRjones"):
        options["stefcal_ifr_gains"] = 1
        options["stefcal_per_chan_ifr_gains"] = 1
    
    gains = {
        "Gjones" : "gain",
        "DDjones" : "diffgain",
        "IFRjones" : "ifrgain"
    }

    reset = jdict.get("reset", None)
    if reset :
        if isinstance(reset, (str, unicode)):
            reset = map(str, reset.split(","))

        for item in reset:
            if item =="all":
                kw["reset"] = True
                break
            else:
                kw["%s_reset"%gains[item]] = True

            if item == "IFRjones":
                options["stefcal_reset_ifr_gains"] = 1
                options["stefcal_ifr_gain_reset"] = 1

    apply_ = jdict.get("apply", None)
    if apply_ :
        if isinstance(apply_, (str, unicode)):
            apply_ = map(str, apply_.split(","))

        if "IFRjones" in apply_:
            options["stefcal_ifr_gains"] = 1
            options["stefcal_per_chan_ifr_gains"] = 1
            options["stefcal_reset_ifr_gains"] = 0
            options["stefcal_ifr_gain_reset"] = 0

        for item in apply_:
            kw["reset"] = False
            if item=="all":
                kw["gain_apply_only"] = True
                kw["ifrgain_apply_only"] = True
                kw["diffgain_apply_only"] = True
                # make sure gains are not reset
                kw["gain_reset"] = False
                kw["ifrgain_reset"] = False
                kw["diffgain_reset"] = False
                break
            else:
                kw["%s_apply_only"%gains[item]] = True
                kw["%s_reset"%gains[item]] = False

    # Include UV model if specified
    if jdict.pop("add_uvmodel", False):
        options.update( {'read_ms_model':1, 'ms_sel.model_column':'MODEL_DATA'} )

    args = map(str, jdict.get("args", [""]))
    reset = kw.pop("reset", True)

    stefcal.stefcal(section="stefcal", reset=reset,
                    dirty=False, 
                    diffgains=DDjones,
                    options=options,
                    output=jdict.get("output", "CORR_RES"),
                    args = args,
                    **kw)

 
def azishe():
    jdict = readJson(CONFIG)
    
    global MULTI
    msnames = jdict.get("msnames", jdict["msname"])
    lsmnames = jdict.get("skymodels", jdict["skymodel"])

    if isinstance(msnames, (str, unicode)):
        msnames = [str(msnames)]
    elif len(msnames)>1:
        MULTI = True

    if isinstance(lsmnames, (str, unicode)):
        lsmnames = [str(lsmnames)]
	

    if len(lsmnames)==1:
        lsmnames = lsmnames*len(msnames)

    v.ITER_List = [ map(str, [msname, lsmname]) for (msname, lsmname) in zip(msnames, lsmnames) ]

    cores = jdict.get("ncpu", 1)
    Pyxis.Context["JOBS"] = cores

    pper("ITER", lambda: calibrate(jdict))
