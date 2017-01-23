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

cab = utils.readJson(CONFIG)

_params = cab['parameters']

params = {}
options = {}
for param in _params:
    if param['value'] is None:
        continue
    params[param['name']] = param['value']

options["ms_sel.ddid_index"] = params.get('spw-id', 0)
options["ms_sel.field_index"] = params.get('field-id', 0)

tdlconf = params.get("tdlconf", None) or  "/code/tdlconf.profiles"
section = params.get("section", None) or 'sim'
mode = params.pop("mode", None) or "simulate"
threads = params.pop("threads", 4)
skymodel = params.pop("skymodel", None)
beam_files_pattern = params.pop("beam-files-pattern", False)

if not os.path.exists(skymodel):
    skymodel = "/data/skymodels/%s"%(os.path.basename(skymodel))
    if not os.path.exists(skymodel):
        raise RuntimeError("ABORT: Could not find the skymodel")

modes = {
    "simulate"  :   '"sim only"',
    "add"       :   "'add to MS'",
    "subtract"  :   "'subtract from MS'",
}

column = params.pop("column", "CORRECTED_DATA")
incol = params.pop("input-column", "CORRECTED_DATA")

msname = params['msname']
options["ms_sel.msname"] = msname
options["sim_mode"] = modes[mode]
options["ms_sel.input_column"] = incol
options["ms_sel.output_column"] = column
options["tiggerlsm.filename"] = skymodel

addnoise = params.pop("addnoise", False)
if addnoise:
    noise = params.pop("noise", 0) or utils.compute_vis_noise(msname, params.pop("sefd", 551))
    options["noise_stddev"] = noise

gjones = params.pop("Gjones", False)
if gjones:
    gain_opts = {
        "me.g_enable"   :   1,
        "oms_gain_models.err-gain.error_model"  :   "SineError",
        "oms_gain_models.err-gain.max_period"   : params.pop("gain-max-period", 2),
        "oms_gain_models.err-gain.maxval"   : params.pop("gain-max-error", 1.2),
        "oms_gain_models.err-gain.min_period"   : params.pop("gain-min-period", 1),
        "oms_gain_models.err-gain.minval"   : params.pop("gain-min-error", 0.8),
    }

    options.update(gain_opts)

    phase_opts = {
        "oms_gain_models.err-phase.error_model" : "SineError",
        "oms_gain_models.err-phase.max_period"  : params.pop("phase-max-period", 2),
        "oms_gain_models.err-phase.maxerr"  : params.pop("phase-max-error", 30.0),
        "oms_gain_models.err-phase.min_period"  : params.pop("phase-min-period", 1),
        "oms_gain_models.err-phase.minval"  : params.pop("phase-min-error", 5),
    }
    
    options.update(phase_opts)

beam = params.pop("Ejones", False)
if beam and beam_files_pattern:
    beam_opts = {
        "me.e_enable"   : 1,
        "me.p_enable"   : 1,
        "me.e_module"   : "Siamese_OMS_pybeams_fits",
        "me.e_all_stations" : 1,
        "pybeams_fits.l_axis"   : params.pop("beam-l-axis", "L"),
        "pybeams_fits.m_axis"   : params.pop("beam-m-axis", "M"),
        "pybeams_fits.filename_pattern" : "'{}'".format(beam_files_pattern),
    }
    options.update(beam_opts)

    rms_perr = params.get("pointing-accuracy", 0)
    # Include pointing errors if needed
    if rms_perr:
        anttab = table(msname + "/" + "ANTENNA")
        NANT = anttab.nrows()
        
        options["me.epe_enable"] = 1
        perr = numpy.random.randn(NANT)*rms_perr, numpy.random.randn(NANT)*rms_perr
        ll, mm = " ".join( map(str, perr[0]) ), " ".join( map(str, perr[-1]) )
        options['oms_pointing_errors.pe_l.values_str'] = "'%s'"%ll
        options['oms_pointing_errors.pe_l.values_str'] = "'%s'"%mm

field_center = params.pop("field-center", None)
if field_center:
    if field_center.lower() == "ms":
        ftab = table(msname+"/FIELD")
        ra,dec = ftab.getcol("PHASE_DIR")[field_id][0]
        field_center = "J2000,%frad,%frad"%(ra, dec)
    tmp = "recentered_"+os.path.basename(skymodel)

    utils.xrun("tigger-convert", ["--recenter", field_center, skymodel, tmp, "-f"])
    options["tiggerlsm.filename"] = tmp

prefix = ["--mt {0} -c {1} [{2}]".format(threads, tdlconf, section)]
suffix = ["%s/Siamese/turbo-sim.py =_tdl_job_1_simulate_MS"%os.environ["MEQTREES_CATTERY_PATH"]]

args = ["%s=%s"%(key, val) for key,val in options.iteritems()]
utils.xrun(cab['binary'], prefix + args + suffix)
