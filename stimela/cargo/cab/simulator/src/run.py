import os
import sys
from pyrap.tables import table

sys.path.append("/utils")
import utils
import numpy

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]
CODE = "/code/"

jdict = utils.readJson(CONFIG)
cab_dict_update = utils.cab_dict_update

msname = jdict.pop("msname")
msname = MSDIR + "/" + msname

field_id = jdict.pop("field_id", 0)
spw_id = jdict.pop("spw_id", 0)
jdict = cab_dict_update(jdict, "ms_sel.ddid_index", spw_id)
jdict = cab_dict_update(jdict, "ms_sel.field_index", field_id)

tdl = jdict.pop("tdlconf", None) or "${CODE}/tdlconf.profiles"
section = jdict.pop("section", None) or "sim"
mode = jdict.pop("mode", "simulate")
threads = jdict.pop("threads", 4)
skymodel = jdict.pop("skymodel", None)
beam_files_pattern = jdict.pop("beam_files_pattern", False)


for item in "skymodel tdl beam_files_pattern".split():
    if isinstance(globals()[item], str):
        globals()[item] = utils.substitute_globals(globals()[item]) or INPUT + "/" + globals()[item]

modes = {
    "simulate"  :   '"sim only"',
    "add"       :   "'add to MS'",
    "subtract"  :   "'subtract from MS'",
}

column = jdict.pop("column", "CORRECTED_DATA")
incol = jdict.pop("input_column", "CORRECTED_DATA")

jdict["ms_sel.msname"] = msname
jdict = cab_dict_update(jdict, "sim_mode", modes[mode])
jdict = cab_dict_update(jdict, "ms_sel.input_column", incol)
jdict = cab_dict_update(jdict, "ms_sel.output_column", column)
jdict["tiggerlsm.filename"] = skymodel

addnoise = jdict.pop("addnoise", False)
if addnoise:
    noise = jdict.pop("noise", 0) or utils.compute_vis_noise(msname, jdict.pop("sefd", 551))
    jdict = cab_dict_update(jdict, "noise_stddev", noise)

gjones = jdict.pop("Gjones", False)
if gjones:
    gain_opts = {
        "me.g_enable"   :   1,
        "oms_gain_models.err-gain.error_model"  :   "SineError",
        "oms_gain_models.err-gain.max_period"   : jdict.pop("gain_max_period", 2),
        "oms_gain_models.err-gain.maxval"   : jdict.pop("gain_max_error", 1.2),
        "oms_gain_models.err-gain.min_period"   : jdict.pop("gain_min_period", 1),
        "oms_gain_models.err-gain.minval"   : jdict.pop("gain_min_error", 0.8),
    }

    jdict = cab_dict_update(jdict, options=gain_opts)

    phase_opts = {
        "oms_gain_models.err-phase.error_model" : "SineError",
        "oms_gain_models.err-phase.max_period"  : jdict.pop("phase_max_period", 2),
        "oms_gain_models.err-phase.maxerr"  : jdict.pop("phase_max_error", 30.0),
        "oms_gain_models.err-phase.min_period"  : jdict.pop("phase_min_period", 1),
        "oms_gain_models.err-phase.minval"  : jdict.pop("phase_min_error", 5),
    }
    
    jdict = cab_dict_update(jdict, options=phase_opts)

beam = jdict.pop("Ejones", False)
if beam and beam_files_pattern:
    beam_opts = {
        "me.e_enable"   : 1,
        "me.p_enable"   : 1,
        "me.e_module"   : "Siamese_OMS_pybeams_fits",
        "me.e_all_stations" : 1,
        "pybeams_fits.l_axis"   : jdict.pop("beam_l_axis", "L"),
        "pybeams_fits.m_axis"   : jdict.pop("beam_m_axis", "M"),
        "pybeams_fits.filename_pattern" : beam_files_pattern,
    }
    jdict = cab_dict_update(jdict, options=beam_opts)

    rms_perr = jdict.get("pointing_accuracy", 0)
    # Include pointing errors if needed
    if rms_perr:
        anttab = table(msname + "/" + "ANTENNA")
        NANT = anttab.nrows()
        
        jdict = cab_dict_update(jdict, "me.epe_enable", 1)
        perr = numpy.random.randn(NANT)*rms_perr, numpy.random.randn(NANT)*rms_perr
        ll, mm = " ".join( map(str, perr[0]) ), " ".join( map(str, perr[-1]) )
        jdict = cab_dict_update(jdict, key='oms_pointing_errors.pe_l.values_str',  value="'%s'"%ll)
        jdict = cab_dict_update(jdict, key='oms_pointing_errors.pe_l.values_str',  value="'%s'"%mm)

field_center = jdict.pop("field_center", None)
if field_center:
    if field_center.lower() == "ms":
        ftab = table(msname+"/FIELD")
        ra,dec = ftab.getcol("PHASE_DIR")[field_id][0]
        field_center = "J2000,%frad,%frad"%(ra, dec)
    tmp = INPUT +"/"+ os.path.basename(skymodel)

    utils.xrun("tigger-convert", ["--recenter",field_center, skymodel, tmp, "-f"])
    jdict["tiggerlsm.filename"] = tmp

prefix = ["--mt %d -c %s [%s]"%(threads, tdl, section)]
suffix = ["%s/Siamese/turbo-sim.py =_tdl_job_1_simulate_MS"%os.environ["MEQTREES_CATTERY_PATH"]]
options = ["%s=%s"%(key, val) for key,val in jdict.iteritems()]
utils.xrun("meqtree-pipeliner.py", prefix + options + suffix)
