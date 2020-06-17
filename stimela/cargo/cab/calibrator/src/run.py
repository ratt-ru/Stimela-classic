import numpy
import os
import sys
from pyrap.tables import table
import subprocess
import Cattery
from scabha import config, parameters_dict, prun, OUTPUT, log

CODE = os.path.join(os.environ["STIMELA_MOUNT"], "code")
CONFIG = os.environ["CONFIG"]

binary = config.binary

jdict = {}
for name, value in parameters_dict.items():
    if value is None:
        continue
    if value is False:
        value = 0
    elif value is True:
        value = 1

    jdict[name] = value

msname = jdict['msname']
THREADS = jdict.pop('threads', 2)
msbase = os.path.basename(msname)[:-3]
prefix = jdict.pop('prefix', None) or '{0}/{1}'.format(OUTPUT, msbase)
params = {}

# options for writing flags
writeflags = jdict.pop("write-flags-to-ms", None)
if writeflags:
    params["ms_sel.ms_write_flags"] = 1
    params["ms_sel.ms_fill_legacy_flags"] = 1 if jdict.pop(
        "fill-legacy-flags", False) else 0

write_flagset = jdict.pop("write-flagset", None)
if write_flagset:
    params["ms_wfl.write_bitflag"] = write_flagset
    params["ms_sel.ms_write_flag_policy"] = "'add to set'" if jdict.pop(
        "write-flag-policy", False) else "'replace set'"

# Read flags options
readflagsets = jdict.pop("read-flagsets", False)
if readflagsets:
    params["ms_rfl.read_flagsets"] = readflagsets

params['ms_sel.ms_read_flags'] = 1 if jdict.pop(
    "read-flags-from-ms", False) else 0
params["ms_rfl.read_legacy_flags"] = 1 if jdict.pop(
    "read-legacy-flags", False) else 0

params["ms_sel.msname"] = msname
field_id = jdict.pop("field-id", 0)
spw_id = jdict.pop("spw-id", 0)
params["ms_sel.tile_size"] = jdict.pop("tile-size", 16)
params["ms_sel.ddid_index"] = spw_id
params["ms_sel.field_index"] = field_id

TDL = jdict.pop("tdlconf", None) or CODE + "/tdlconf.profiles"
SECTION = jdict.pop("section", None) or "stefcal"
skymodel = jdict.pop("skymodel", None)
beam_files_pattern = jdict.pop("beam-files-pattern", False)
jones_type = jdict.pop("jones-implementation", "Gain2x2")

column = jdict.pop("column", "DATA")
outcol = jdict.pop("output-column", "CORRECTED_DATA")

params["ms_sel.input_column"] = column
params["ms_sel.output_column"] = outcol
params["tiggerlsm.filename"] = skymodel
params["tiggerlsm.lsm_subset"] = jdict.get("subset", "all")
params["do_output"] = jdict.pop("output-data", "CORR_RES")
saveconf = jdict.pop('save-config', None)
params['ms_sel.ms_corr_sel'] = "'{}'".format(jdict.pop('correlations', '2x2'))

label = jdict.pop("label", None)

model_column = jdict.pop("model-column", 'MODEL_DATA')

gjones = jdict.pop("Gjones", False)
if gjones:

    time_smooth, freq_smooth = jdict.get("Gjones-smoothing-intervals", (1, 1))
    time_int, freq_int = jdict.get("Gjones-solution-intervals", (1, 1))
    mode = 'apply' if jdict.get('Gjones-apply-only', False) else 'solve-save'

    gjones_gains = jdict.pop('Gjones-gain-table', None) or "{0}/{1}{2}.gain.cp".format(
        OUTPUT, msbase, "-%s" % label if label else "")
    params.update({
        "stefcal_gain.enabled": 1,
        "stefcal_gain.mode": mode,
        "stefcal_gain.reset": 0 if mode == "apply" else 1,
        "stefcal_gain.implementation": jones_type,
        "stefcal_gain.timeint": time_int,
        "stefcal_gain.freqint": freq_int,
        "stefcal_gain.flag_ampl":   jdict.get("Gjones-ampl-clipping", 0),
        "stefcal_gain.flag_chisq":   jdict.get("Gjones-chisq-clipping", 0),
        "stefcal_gain.flag_chisq_threshold":   jdict.get("Gjones-thresh-sigma", 10),
        "stefcal_gain.flag_ampl_low":   jdict.get("Gjones-ampl-clipping-low", 0.3),
        "stefcal_gain.flag_ampl_high":   jdict.get("Gjones-ampl-clipping-high", 2),
        "stefcal_gain.implementation":   jdict.get("Gjones-matrix-type", "Gain2x2"),
        "stefcal_gain.table": gjones_gains,
    })

bjones = jdict.pop("Bjones", False)
if bjones:

    time_smooth, freq_smooth = jdict.get("Bjones-smoothing-intervals", (1, 0))
    time_int, freq_int = jdict.get("Bjones-solution-intervals", (1, 0))
    mode = 'apply' if jdict.get('Bjones-apply-only', False) else 'solve-save'

    bjones_gains = jdict.pop('Bjones-gain-table', None) or "{0}/{1}{2}.gain1.cp".format(
        OUTPUT, msbase, "-%s" % label if label else "")
    params.update({
        "stefcal_gain1.enabled": 1,
        "stefcal_gain1.label": 'B',
        "stefcal_gain1.mode": mode,
        "stefcal_gain1.reset": 0 if mode == "apply" else 1,
        "stefcal_gain1.implementation": jones_type,
        "stefcal_gain1.timeint": time_int,
        "stefcal_gain1.freqint": freq_int,
        "stefcal_gain1.flag_ampl":   jdict.get("Bjones-ampl-clipping", 0),
        "stefcal_gain1.flag_chisq":   jdict.get("Bjones-chisq-clipping", 0),
        "stefcal_gain1.flag_chisq_threshold":   jdict.get("Bjones-thresh-sigma", 10),
        "stefcal_gain1.flag_ampl_low":   jdict.get("Bjones-ampl-clipping-low", 0.3),
        "stefcal_gain1.flag_ampl_high":   jdict.get("Bjones-ampl-clipping-high", 2),
        "stefcal_gain1.implementation":   jdict.get("Bjones-matrix-type", "Gain2x2"),
        "stefcal_gain1.table": bjones_gains,
    })

beam = jdict.pop("Ejones", False)
if beam and beam_files_pattern:
    params.update({
        "me.e_enable": 1,
        "me.p_enable": 1,
        "me.e_module": "Siamese_OMS_pybeams_fits",
        "me.e_all_stations": 1,
        "pybeams_fits.sky_rotation":  1 if jdict.pop('parallactic-angle-rotation', False) else 0,
        "pybeams_fits.l_axis": jdict.pop("beam-l-axis", "L"),
        "pybeams_fits.m_axis": jdict.pop("beam-m-axis", "M"),
        "pybeams_fits.filename_pattern": "'{}'".format(beam_files_pattern),
    })


ddjones = jdict.pop("DDjones", False)
if ddjones:
    time_int, freq_int = jdict.pop("DDjones-solution-intervals", (1, 1))
    time_smooth, freq_smooth = jdict.pop("DDjones-smoothing-intervals", (1, 1))

    mode = 'apply' if jdict.get('DDjones-apply-only', False) else 'solve-save'

    ddjones_gains = jdict.pop('DDjones-gain-table', None) or "{0}/{1}{2}.diffgain.cp".format(
        OUTPUT, msbase, "-%s" % label if label else "")
    params.update({
        "stefcal_diffgain.enabled": 1,
        "stefcal_diffgain.reset": 0 if mode == "apply" else 1,
        "stefcal_diffgain.flag_ampl": 0,
        "stefcal_diffgain.flag_chisq": 1,
        "stefcal_diffgain.flag_chisq_threshold": 5,
        "stefcal_diffgain.freqint": freq_int,
        "stefcal_diffgain.freqsmooth": freq_smooth,
        "stefcal_diffgain.implementation": jones_type,
        "stefcal_diffgain.label": jdict.pop("DDjones-tag", "dE"),
        "stefcal_diffgain.max_diverge": 1,
        "stefcal_diffgain.mode": mode,
        "stefcal_diffgain.niter": 50,
        "stefcal_diffgain.omega": 0.5,
        "stefcal_diffgain.quota": 0.95,
        "stefcal_diffgain.table": ddjones_gains,
        "stefcal_diffgain.timeint": time_int,
        "stefcal_diffgain.timesmooth": time_smooth,
        "stefcal_diffgain.implementation":   jdict.get("DDjones-matrix-type", "Gain2x2"),
    })

ifrjones = jdict.pop("DDjones", False)
if ifrjones:
    ifrjones_gains = jdict.pop('IFRjones-gain-table', None) or "{0}/{1}{2}.ifrgain.cp".format(
        OUTPUT, msbase, "-%s" % label if label else "")
    mode = 'apply' if jdict.get('IFRjones-apply-only', False) else 'solve-save'

    params.update({
        "stefcal_ifr_gain_mode": mode,
        "stefcal_ifr_gains": 1,
        "stefcal_ifr_gain_reset": 0 if mode == "apply" else 1,
        "stefcal_reset_ifr_gains": 0 if mode == "apply" else 1,
        "stefcal_ifr_gain.table": ifrjones_gains,
    })

makeplots = jdict.pop("make-plots", False)

gjones_plotprefix = prefix+"-gjones_plots"
bjones_plotprefix = prefix+"-bjones_plots"
ddjones_plotprefix = prefix+"-ddjones_plots"
ifrjones_plotprefix = prefix+"-ifrjones_plots"


def run_meqtrees(msname):

    prefix = ["--mt %d -c %s [%s]" % (THREADS, TDL, SECTION)]
    CATTERY_PATH = os.path.dirname(Cattery.__file__)
    suffix = ["%s/Calico/calico-stefcal.py =stefcal" % CATTERY_PATH]
    options = {}
    options.update(params)
    if jdict.pop("add-vis-model", 0):
        options["read_ms_model"] = 1
        options["ms_sel.model_column"] = model_column

    taql = jdict.get('data-selection', None)
    if taql:
        options["ms_sel.ms_taql_str"] = taql

    args = []
    for key, value in options.items():
        if isinstance(value, str) and value.find(' ') > 0:
            value = '"{:s}"'.format(value)
        args.append('{0}={1}'.format(key, value))

    args = prefix + args + suffix

    _runc = " ".join([binary] + args + \
            ['-s {}'.format(saveconf) if saveconf else ''])
    if prun(_runc) !=0:
        sys.exit(1)

    log.info("MeqTrees Done!")
    # now plot the gains
    if makeplots:
        log.info("Preparing to make gain plots")
        import Owlcat.Gainplots as plotgains
        feed_tab = table(msname+"/FEED")
        log.info("Extracting feed type from MS")
        feed_type = set(feed_tab.getcol("POLARIZATION_TYPE")['array'])
        feed_type = "".join(feed_type)
        log.info("Feed type is [%s]" % feed_type)

        if feed_type.upper() in ["XY", "YX"]:
            feed_type = "XY"
        else:
            feed_type = "RL"

        if gjones:
            log.info("Making Gain plots (G)...")
            plotgains.make_gain_plots(
                gjones_gains, prefix=gjones_plotprefix, feed_type=feed_type)

        if bjones:
            log.info("Making Gain plots (B)...")
            plotgains.make_gain_plots(
                bjones_gains, gain_label='B', prefix=bjones_plotprefix, feed_type=feed_type)

        if ddjones:
            log.info("Making differential gain plots...")
            plotgains.make_diffgain_plots(
                ddjones_gains, prefix=ddjones_plotprefix, feed_type=feed_type)

        if ifrjones:
            log.info("Making IFR gain plots...")
            plotgains.make_ifrgain_plots(
                ifrjones_gains, prefix=ifrjones_plotprefix, feed_type=feed_type)

run_meqtrees(msname)
