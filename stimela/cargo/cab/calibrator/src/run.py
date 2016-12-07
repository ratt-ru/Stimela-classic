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

jdict = utils.readJson(CONFIG)
cab_dict_update = utils.cab_dict_update



msname = jdict.pop("msname")
msname = MSDIR + "/" + msname

field_id = jdict.pop("field_id", 0)
spw_id = jdict.pop("spw_id", 0)
jdict = cab_dict_update(jdict, "ms_sel.ddid_index", spw_id)
jdict = cab_dict_update(jdict, "ms_sel.field_index", field_id)

tdl = jdict.pop("tdlconf", None) or "/code/tdlconf.profiles"
section = jdict.pop("section", None) or "stefcal"
threads = jdict.pop("threads", 4)
skymodel = jdict.pop("skymodel", None)
beam_files_pattern = jdict.pop("beam_files_pattern", False)
jones_type = jdict.pop("jones_implementation", "Gain2x2")

for item in "skymodel tdl beam_files_pattern".split():
    if not isinstance(globals()[item], (str, unicode)):
        continue
    found = False
    for place in INPUT, OUTPUT, MSDIR, "/code/", "/data/skymodels/":
        if globals()[item].startswith(place):
            found = True
            break
    if not found:
        globals()[item] = INPUT +"/"+ globals()[item]


column = jdict.pop("column", "DATA")
outcol = jdict.pop("output", "CORRECTED_DATA")

jdict["ms_sel.msname"] = msname
jdict = cab_dict_update(jdict, "ms_sel.input_column", column)
jdict = cab_dict_update(jdict, "ms_sel.output_column", outcol)
jdict["tiggerlsm.filename"] = skymodel
label = jdict.pop("label", None)


apl = jdict.pop("apply", None)
if isinstance(apl, str):
    apl = [apl]

if apl:
    modes = {
        "Gjones"    :   "solve-save" if "Gjones" in apl else "apply",
        "DDjones"   :   "solve-save" if "DDjones" in apl else "apply",
        "IFRjones"  :   "solve-save" if "IFRjones" in apl else "apply",
    }
else:
    modes = dict(Gjones="solve-save", DDjones="solve-save", IFRjones="solve-save")

gjones = jdict.pop("Gjones", False)
if gjones:

    time_smooth, freq_smooth = jdict.get("Gjones_smoothing", (10,10))
    time_int, freq_int = jdict.get("Gjones_intervals", (10,10))

    gjones_gains = "%s%s.gain.cp"%(msname[:-3], "-%s"%label if label else "")
    gjones_opts = {
        "stefcal_gain.mode" : modes["Gjones"],
        "stefcal_gain.implementation" : jones_type,
        "tiggerlsm.lsm_subset"  : jdict.get("subset", "all"),
        "stefcal_gain.timeint"  : time_int,
        "stefcal_gain.freqint"  : freq_int,
        "stefcal_diffgain.freqsmooth" : freq_smooth,
        "stefcal_diffgain.timesmooth" : time_smooth,
        "stefcal_gain.flag_ampl"    :   jdict.get("Gjones_ampl_clipping", 0),
        "stefcal_gain.flag_chisq"   :   jdict.get("Gjones_chisq_clipping", 0),
        "stefcal_gain.flag_chisq_threshold" :   jdict.get("Gjones_thresh_sigma", 10),
        "stefcal_gain.flag_ampl_low"    :   jdict.get("Gjones_flag_ampl_low", 0.3),
        "stefcal_gain.flag_ampl_high"   :   jdict.get("Gjones_flag_ampl_high", 2),
        "stefcal_gain.table" : gjones_gains,
    }
    
    jdict = cab_dict_update(jdict, options=gjones_opts)

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

ddjones = jdict.pop("DDjones", False)
if ddjones:
    options["stefcal_diffgain.flag_ampl"] = 0
    options["stefcal_diffgain.flag_chisq"] = 0
    freq_int, freq_smooth = jdict.get("DDjones_intervals", None)
    time_smooth, freq_smooth = jdict.get("DDjones_smoothing", None)

    ddjones_gains = "%s%s.diffgain.cp"%(msname[:-3], "-%s"%label if label else "")
    ddjones_opts = {
        "stefcal_diffgain.enabled" : 1,
        "stefcal_diffgain.flag_ampl" : 0,
        "stefcal_diffgain.flag_chisq" : 1,
        "stefcal_diffgain.flag_chisq_threshold" : 5,
        "stefcal_diffgain.freqint" : freq_int,
        "stefcal_diffgain.freqsmooth" : freq_smooth,
        "stefcal_diffgain.implementation" : jones_type,
        "stefcal_diffgain.label" : dd_label,
        "stefcal_diffgain.max_diverge" : 1,
        "stefcal_diffgain.mode" : modes["DDjones"],
        "stefcal_diffgain.niter" : 50,
        "stefcal_diffgain.omega" : 0.5,
        "stefcal_diffgain.quota" : 0.95,
        "stefcal_diffgain.table" : ddjones_gains,
        "stefcal_diffgain.timeint" : time_int,
        "stefcal_diffgain.timesmooth" : time_smooth,
}
    jdict = cab_dict_update(jdict, options=ddjones_opts)

ifrjones = jdict.pop("DDjones", False)
if ifrjones:
    ifrjones_gains = "%s%s.ifrgain.cp"%(msname[:-3], "-%s"%label if label else "")
    ifrjones_opts = {
        "stefcal_ifr_gain_mode" : modes["IFRgain"],
        "stefcal_ifr_gains" : 1,
        "stefcal_ifr_gain_reset" : 0 if modes["IFRgain"]=="apply" else 1,
        "stefcal_ifr_gain.table" : ifrjones_gains,
        "stefcal_ifr_gains" : 1,
    }
    jdict = cab_dict_update(jdict, options=ifrjones_opts)

makeplots = jdict.pop("plotgains", False)
pp = "%s/%s"%(OUTPUT, os.path.basename(msname)[:-3])
gjones_plotprefix = jdict.pop("Gjones_plotprefix", pp+"-gjones_plots")
ddjones_plotprefix = jdict.pop("DDjones_plotprefix", pp+"ddjones_plots")
ifrjones_plotprefix = jdict.pop("IFRjones_plotprefix", pp+"ifrjones_plots")

prefix = ["--mt %d -c %s [%s]"%(threads, tdl, section)]
suffix = ["%s/Calico/calico-stefcal.py =stefcal"%os.environ["MEQTREES_CATTERY_PATH"]]
options = ["%s=%s"%(key, val) for key,val in jdict.iteritems()]

utils.xrun("meqtree-pipeliner.py", prefix + options + suffix)

# now plot the gains
if makeplots:
    import Owlcat.Gainplots as plotgains
    feed_tab = table(msname+"/FEED")
    feed_type = set(feed_tab.getcol("POLARIZATION_TYPE")['array'])
    feed_type = "".join(feed_type)

    if feed_type.upper() in ["XY", "YX"]:
        feed_type = "XY"
    else:
        feed_type = "RL"

    if modes["Gjones"] == "solve-save" and gjones:
        plotgains.make_gain_plots(gjones_gains, prefix=gjones_plotprefix, feed_type=feed_type)

    if modes["DDjones"] == "solve-save" and ddjones:
        plotgains.make_diffgain_plots(ddjones_gains, prefix=ddjones_plotprefix, feed_type=feed_type)

    if modes["IFRjones"] == "solve-save" and ifrjones:
        plotgains.make_ifrgain_plots(ifrjones_gains, prefix=ifrjones_plotprefix, feed_type=feed_type)
