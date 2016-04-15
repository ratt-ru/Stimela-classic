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



def calibrate(jdict):

    v.LOG = II("${OUTDIR>/}log-${MS:BASE}-calibration.txt")

    x.sh("addbitflagcol $MS")

    ms.set_default_spectral_info()

    prefix = jdict.get("prefix", None)

    for item in [INDIR, "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = lsmname

    column = jdict.get("column", "DATA")

    ms.DDID = jdict.get("spw_id", 0)
    ms.FIELD = jdict.get("field_id", 0)

    options = {}
    options["tiggerlsm.lsm_subset"] = jdict.get("subset", "all")
    gtimeint, gfreqint = jdict.get("Gjones_intervals", (1,1))

    options["stefcal_gain.timeint"] = gtimeint
    options["stefcal_gain.freqint"] = gfreqint
    options["stefcal_gain.flag_ampl"] = jdict.get("gjones_ampl_clipping", 0)
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
        options["pybeams_fits.l_axis"] = jdict.get("beam_l_axis", "L")
        options["pybeams_fits.m_axis"] = jdict.get("beam_m_axis", "M")
        options["pybeams_fits.filename_pattern"] =  "%s/%s"%(INDIR, jdict["beam_files_pattern"])

    options["ms_sel.input_column"] = column

    DDjones = jdict.get("DDjones", False)

    if jdict.get("IFR_gains"):
        options["stefcal_ifr_gains"] = 1
    
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
                options["stefcal_reset_all"] = True
                break
            else:
                options["%s_reset"%gains[item]] = True


    apply_ = jdict.get("apply", None)
    if apply_ :
        if isinstance(apply_, (str, unicode)):
            apply_ = map(str, apply_.split(","))
    
        for item in apply_:
            if item=="all":
                options["gain_apply_only"] = True
                options["ifrgain_apply_only"] = True
                options["diffgain_apply_only"] = True
                break
            else:
                options["%s_apply_only"%gains[item]] = True

    # Include UV model if specified
    if jdict.pop("add_uvmodel", False):
        options.update( {'read_ms_model':1,'ms_sel.model_column':'MODEL_DATA'} )

    stefcal.stefcal(section="stefcal", gain_plot_prefix=prefix,
                    reset=True, dirty=False, 
                    diffgains=DDjones,
                    options=options,
                    output=jdict.get("output_column", "CORR_RES"))

 
def azishe():
    jdict = readJson(CONFIG)

    msnames = jdict.get("msnames", jdict["msname"])

    if isinstance(msnames, (str, unicode)):
        msnames = [str(msnames)]


    v.MS_List = ["{:s}/{:s}".format(MSDIR, msname) for msname in msnames]

    cores = jdict.get("cpus", 1)
    Pyxis.Context["JOBS"] = cores

    per_ms(lambda: calibrate(jdict))
