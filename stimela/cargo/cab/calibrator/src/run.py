import os
import sys
from pyrap.tables import table
import subprocess

sys.path.append("/utils")
import utils
import numpy

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]
CODE = "/code"

cab = utils.readJson(CONFIG)
binary = cab['binary']
parameters = cab['parameters']

jdict = {}
for param in parameters:
    name = param['name']
    value = param['value']
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

params["ms_sel.msname"] = msname
field_id = jdict.pop("field-id", 0)
spw_id = jdict.pop("spw-id", 0)
params["ms_sel.ddid_index"] = spw_id
params["ms_sel.field_index"] = field_id

TDL = jdict.pop("tdlconf", None) or "/code/tdlconf.profiles"
SECTION = jdict.pop("section", None) or "stefcal"
skymodel = jdict.pop("skymodel", None)
beam_files_pattern = jdict.pop("beam-files-pattern", False)
jones_type = jdict.pop("jones-implementation", "Gain2x2")

column = jdict.pop("column", "DATA")
outcol = jdict.pop("output", "CORRECTED_DATA")

params["ms_sel.input_column"] = column
params["ms_sel.output_column"] = outcol
params["tiggerlsm.filename"] = skymodel
params["do_output"] = jdict.pop("output-data", "CORR_RES")

label = jdict.pop("label", None)

gjones = jdict.pop("Gjones", False)
if gjones:

    time_smooth, freq_smooth = params.get("Gjones-smoothing", (1,1))
    time_int, freq_int = jdict.get("Gjones-intervals", (1,1))
    mode = 'apply' if jdict.get('Gjones-apply-only', False) else 'solve-save'

    gjones_gains = "{0}/{1}{2}.gain.cp".format(msname, msbase, "-%s"%label if label else "")
    params.update( {
        "stefcal_gain.mode" : mode, 
        "stefcal_gain.implementation" : jones_type,
        "tiggerlsm.lsm_subset"  : jdict.get("subset", "all"),
        "stefcal_gain.timeint"  : time_int,
        "stefcal_gain.freqint"  : freq_int,
        "stefcal_diffgain.freqsmooth" : freq_smooth,
        "stefcal_diffgain.timesmooth" : time_smooth,
        "stefcal_gain.flag_ampl"    :   jdict.get("Gjones-ampl-clipping", 0),
        "stefcal_gain.flag_chisq"   :   jdict.get("Gjones-chisq-clipping", 0),
        "stefcal_gain.flag_chisq_threshold" :   jdict.get("Gjones-thresh-sigma", 10),
        "stefcal_gain.flag_ampl_low"    :   jdict.get("Gjones-ampl-clipping-low", 0.3),
        "stefcal_gain.flag_ampl_high"   :   jdict.get("Gjones-ampl-clipping-high", 2),
        "stefcal_gain.table" : gjones_gains,
    })
    
beam = jdict.pop("Ejones", False)
if beam and beam_files_pattern:
    params.update({
        "me.e_enable"   : 1,
        "me.p_enable"   : 1,
        "me.e_module"   : "Siamese_OMS_pybeams_fits",
        "me.e_all_stations" : 1,
        "pybeams_fits.l_axis"   : jdict.pop("beam-l-axis", "L"),
        "pybeams_fits.m_axis"   : jdict.pop("beam-m-axis", "M"),
        "pybeams_fits.filename_pattern" : "'{}'".format(beam_files_pattern),
    })


ddjones = jdict.pop("DDjones", False)
if ddjones:
    freq_int, freq_smooth = jdict.pop("DDjones-solution-intervals", (0,0))
    time_smooth, freq_smooth = jdict.pop("DDjones-smoothing-intervals", (0,0))

    mode = 'apply' if jdict.get('DDjones-apply-only', False) else 'solve-save'

    ddjones_gains = "{0}/{1}{2}.diffgain.cp".format(msname, msbase, "-%s"%label if label else "")
    params.update({
        "stefcal_diffgain.enabled" : 1,
        "stefcal_diffgain.flag_ampl" : 0,
        "stefcal_diffgain.flag_chisq" : 1,
        "stefcal_diffgain.flag_chisq_threshold" : 5,
        "stefcal_diffgain.freqint" : freq_int,
        "stefcal_diffgain.freqsmooth" : freq_smooth,
        "stefcal_diffgain.implementation" : jones_type,
        "stefcal_diffgain.label" : jdict.pop("DDjones-tag", "dE"),
        "stefcal_diffgain.max_diverge" : 1,
        "stefcal_diffgain.mode" : mode,
        "stefcal_diffgain.niter" : 50,
        "stefcal_diffgain.omega" : 0.5,
        "stefcal_diffgain.quota" : 0.95,
        "stefcal_diffgain.table" : ddjones_gains,
        "stefcal_diffgain.timeint" : time_int,
        "stefcal_diffgain.timesmooth" : time_smooth,
})

ifrjones = jdict.pop("DDjones", False)
if ifrjones:
    ifrjones_gains = "{0}/{1}{2}.ifrgain.cp".format(msname, msbase, "-%s"%label if label else "")
    mode = 'apply' if jdict.get('IFRjones-apply-only', False) else 'solve-save'

    params.update({
        "stefcal_ifr_gain_mode" : mode,
        "stefcal_ifr_gains" : 1,
        "stefcal_ifr_gain_reset" : 0 if mode=="apply" else 1,
        "stefcal_ifr_gain.table" : ifrjones_gains,
    })

makeplots = jdict.pop("make-plots", False)

gjones_plotprefix = prefix+"-gjones_plots"
ddjones_plotprefix = prefix+"-ddjones_plots"
ifrjones_plotprefix = prefix+"-ifrjones_plots"

def run_meqtrees(msname):

    prefix = ["--mt %d -c %s [%s]"%(THREADS, TDL, SECTION)]
    suffix = ["%s/Calico/calico-stefcal.py =stefcal"%os.environ["MEQTREES_CATTERY_PATH"]]
    options = {}
    options.update(params)
    if options.pop("add-vis-model", 0):
        options["read_ms_model"] = 1
        options["ms_sel.model_column"] = "MODEL_DATA"

    args = prefix + ["%s=%s"%(key, val) for key,val in options.iteritems()] + suffix

    utils.xrun(cab['binary'], args)
    
    print("MeqTrees Done!")
    # now plot the gains
    if makeplots:
        print("Preparing to make gain plots")
        import Owlcat.Gainplots as plotgains
        feed_tab = table(msname+"/FEED")
        print("Extracting feed type from MS")
        feed_type = set(feed_tab.getcol("POLARIZATION_TYPE")['array'])
        feed_type = "".join(feed_type)
        print("Feed type is [%s]"%feed_type)
    
        if feed_type.upper() in ["XY", "YX"]:
            feed_type = "XY"
        else:
            feed_type = "RL"
    
        if gjones:
            print("Making Gain plots...")
            plotgains.make_gain_plots(gjones_gains, prefix=gjones_plotprefix, feed_type=feed_type)
    
        if ddjones:
            print("Making differential gain plots...")
            plotgains.make_diffgain_plots(ddjones_gains, prefix=ddjones_plotprefix, feed_type=feed_type)
    
        if ifrjones:
            print("Making IFR gain plots...")
            plotgains.make_ifrgain_plots(ifrjones_gains, prefix=ifrjones_plotprefix, feed_type=feed_type)

    sys.exit(0)

run_meqtrees(msname)
