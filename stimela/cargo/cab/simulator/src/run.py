import numpy
import os
import sys
from pyrap.tables import table
import yaml
import math
import Cattery
from scabha import config, parameters_dict, prun

CODE = os.path.join(os.environ["STIMELA_MOUNT"], "code")
CONFIG = os.environ["CONFIG"]

def compute_vis_noise(msname, sefd, spw_id=0):
    """Computes nominal per-visibility noise"""
    tab = table(msname)
    spwtab = table(msname + "/SPECTRAL_WINDOW")

    freq0 = spwtab.getcol("CHAN_FREQ")[spw_id, 0]
    wavelength = 300e+6/freq0
    bw = spwtab.getcol("CHAN_WIDTH")[spw_id, 0]
    dt = tab.getcol("EXPOSURE", 0, 1)[0]
    dtf = (tab.getcol("TIME", tab.nrows()-1, 1)-tab.getcol("TIME", 0, 1))[0]

    # close tables properly, else the calls below will hang waiting for a lock...
    tab.close()
    spwtab.close()

    print(">>> %s freq %.2f MHz (lambda=%.2fm), bandwidth %.2g kHz, %.2fs integrations, %.2fh synthesis" % (
        msname, freq0*1e-6, wavelength, bw*1e-3, dt, dtf/3600))
    noise = sefd/math.sqrt(abs(2*bw*dt))
    print(">>> SEFD of %.2f Jy gives per-visibility noise of %.2f mJy" %
          (sefd, noise*1000))

    return noise

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

_params = parameters_dict

params = {}
options = {}
for name, value in _params.items():

    if value is None:
        continue

    params[name] = value

options["ms_sel.ddid_index"] = params.get('spw-id', 0)
options["ms_sel.field_index"] = params.get('field-id', 0)

tdlconf = params.get("tdlconf", None) or CODE+"/tdlconf.profiles"
section = params.get("section", None) or 'sim'
mode = params.pop("mode", None) or "simulate"
threads = params.pop("threads", 4)
skymodel = params.pop("skymodel", None)
beam_files_pattern = params.pop("beam-files-pattern", False)

if isinstance(skymodel, str):
    if os.path.exists(skymodel):
        options['me.sky.tiggerskymodel'] = 1
        options["tiggerlsm.filename"] = skymodel
    else:
        raise RuntimeError("ABORT: Could not find the skymodel")

modes = {
    "simulate":   'sim only',
    "add":   "add to MS",
    "subtract":   'subtract from MS',
}

column = params.pop("column", "CORRECTED_DATA")
incol = params.pop("input-column", "CORRECTED_DATA")

msname = params['msname']
options["ms_sel.msname"] = msname
options["sim_mode"] = modes[mode]
options["ms_sel.input_column"] = incol
options["ms_sel.output_column"] = column
options["me.use_smearing"] = 1 if params.pop('smearing', False) else 0
saveconf = params.pop('save-config', None)

addnoise = params.pop("addnoise", False)
options["ms_sel.tile_size"] = params.pop("tile-size", 16)

if addnoise:
    noise = params.pop("noise", 0) or compute_vis_noise(
        msname, params.pop("sefd", 551))
    options["noise_stddev"] = noise

gjones = params.pop("Gjones", False)
if gjones:
    gain_opts = {
        "me.g_enable":   1,
        "oms_gain_models.err-gain.error_model":   "SineError",
        "oms_gain_models.err-gain.max_period": params.pop("gain-max-period", 2),
        "oms_gain_models.err-gain.maxval": params.pop("gain-max-error", 1.2),
        "oms_gain_models.err-gain.min_period": params.pop("gain-min-period", 1),
        "oms_gain_models.err-gain.minval": params.pop("gain-min-error", 0.8),
    }

    options.update(gain_opts)

    phase_opts = {
        "oms_gain_models.err-phase.error_model": "SineError",
        "oms_gain_models.err-phase.max_period": params.pop("phase-max-period", 2),
        "oms_gain_models.err-phase.maxerr": params.pop("phase-max-error", 30.0),
        "oms_gain_models.err-phase.min_period": params.pop("phase-min-period", 1),
        "oms_gain_models.err-phase.minval": params.pop("phase-min-error", 5),
    }

    options.update(phase_opts)

beam = params.pop("Ejones", False)
if beam and beam_files_pattern:
    beam_opts = {
        "me.e_enable": 1,
        "me.p_enable": 1,
        "me.e_module": "Siamese_OMS_pybeams_fits",
        "pybeams_fits.sky_rotation":  1 if params.pop('parallactic-angle-rotation', False) else 0,
        "me.e_all_stations": 1,
        "pybeams_fits.l_axis": params.pop("beam-l-axis", "L"),
        "pybeams_fits.m_axis": params.pop("beam-m-axis", "M"),
        "pybeams_fits.filename_pattern": "'{}'".format(beam_files_pattern),
    }
    options.update(beam_opts)

    rms_perr = params.get("pointing-accuracy", 0)
    # Include pointing errors if needed
    if rms_perr:
        anttab = table(msname + "/" + "ANTENNA")
        NANT = anttab.nrows()

        options["me.epe_enable"] = 1
        perr = numpy.random.randn(
            NANT)*rms_perr, numpy.random.randn(NANT)*rms_perr
        ll, mm = " ".join(map(str, perr[0])), " ".join(map(str, perr[-1]))
        options['oms_pointing_errors.pe_l.values_str'] = "'%s'" % ll
        options['oms_pointing_errors.pe_l.values_str'] = "'%s'" % mm

field_center = params.pop("field-center", None)
if field_center and skymodel:
    if field_center.lower() == "ms":
        ftab = table(msname+"/FIELD")
        ra, dec = ftab.getcol("PHASE_DIR")[params.get('field-id', 0)][0]
        field_center = "J2000,%frad,%frad" % (ra, dec)
    tmp = "recentered_"+os.path.basename(skymodel)

    prun(["tigger-convert", "--recenter", field_center, skymodel, tmp, "-f"])
    options["tiggerlsm.filename"] = tmp

prefix = ['-s {}'.format(saveconf) if saveconf else ''] + \
    ["--mt {0} -c {1} [{2}]".format(threads, tdlconf, section)]
CATTERY_PATH = os.path.dirname(Cattery.__file__)
suffix = ["%s/Siamese/turbo-sim.py =_simulate_MS" % CATTERY_PATH]

args = []
for key, value in options.items():
    if isinstance(value, str) and value.find(' ') > 0:
        value = '"{:s}"'.format(value)
    args.append('{0}={1}'.format(key, value))

_runc = " ".join([config.binary] + prefix + args + suffix)

exitcode = prun(_runc)
if exitcode != 0:
    raise RuntimeError(f"Meqtrees failed with exit code {exitcode}. See logs for more details")
