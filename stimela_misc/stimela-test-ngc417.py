import stimela
import os

#I/O
INPUT = 'input'
MSDIR = 'msdir'


MS = '12A-405.sb7601493.eb10633016.56086.127048738424.ms'
PREFIX = 'vla_NGC417_LBand'
# Fields
GCAL = '0'
TARGET = '1'
BPCAL = '2' # 3C286

# Reference antenna
REFANT = 'ea21'

# Calibration tables
ANTPOS_TABLE = PREFIX + '.antpos:output'
BPCAL_TABLE = PREFIX + '.B0:output'
DELAYCAL_TABLE = PREFIX + '.K0:output'
GAINCAL_TABLE = PREFIX + '.G0:output'
FLUXSCALE_TABLE = PREFIX + '.fluxscale:output'
GAINCAL_TABLE2 = PREFIX + '.G1:output'
_nchans = 32


LABEL = "ngc147_reduction"

stimela.register_globals()

OUTPUT = "output_%s"%LABEL

recipe = stimela.Recipe('VLA NGC417 1GC reduction script', ms_dir=MSDIR)

# It is common for the array to require a small amount of time to settle down at the start of a scan. Consequently, it has
# become standard practice to flag the initial samples from the start of each scan. This is known as 'quack' flagging
recipe.add('cab/casa_flagdata', 'quack_flagging', {
        "vis"           :   MS,
        "mode"         :   'quack',
        "quackinterval" :   10.0,
        "quackmode"     :   'beg',
},
    input = INPUT,
    output = OUTPUT,
    label = 'quack_flagging:: Quack flagging')


#Flag the autocorrelations

recipe.add('cab/casa_flagdata', 'autocorr_flagging', {
        "vis"           :   MS,
        "mode"          :   'manual',
        "autocorr"      :   True,
},
    input = INPUT,
    output = OUTPUT,
    label = 'autocorr_flagging:: Autocorrelations flagging')


#Flag bad channels
recipe.add('cab/casa_flagdata', 'badchan_flagging', {
        "vis"           :   MS,
        "mode"          :   'manual',
        "spw"           :   "0:0~20,0:236~256"
},
    input = INPUT,
    output = OUTPUT,
    label = 'badchan_flagging:: Bad Channel flagging')




#Flag potentially pesky antennas
recipe.add('cab/casa_flagdata', 'antenna_flagging', {
        "vis"           :   MS,
        "mode"          :   'manual',
        "antenna"       :   'ea05,ea23,ea26'      
},
    input = INPUT,
    output = OUTPUT,
    label = 'antenna_flagging::Antenna flagging')



#Autoflagging (With Aoflagger) - This is supposed to flag RFI in the data - good to flag prior to 
#starting the calibration process.
recipe.add('cab/autoflagger', 'aoflag_data', {
        "msname"    :   MS,
        "column"    :   "DATA",
},    
    input=INPUT,
    output=OUTPUT,    
    label='aoflag_data:: Flag DATA column')

# Lets make some diagnostic plots
recipe.add('cab/casa_plotms', 'plot_manual', {
        "vis"           :   MS,
        "plotfile"      :   PREFIX + 'after_manual_flags.png',
        "selectdata"    :    True,
        "correlation"   :   'RR,LL',
        "averagedata"   :   True,
        "avgchannel"    :   '64',
        "coloraxis"     :   'field',
        "overwrite"     :   True,
},
    input = INPUT,
    output = OUTPUT,
    label = 'plot_manual:: Plot data after manual flagging')


# Plot amplitude vs uv distance
recipe.add('cab/casa_plotms', 'plot_amp_uvdist', {
        "vis"           :   MS,
        "plotfile"      :   PREFIX + 'initial_amp_uvdist.png',
        "xaxis"         :   "uvdist",
        "yaxis"         :   "amp",
        "selectdata"    :    True,
        "correlation"   :   'RR,LL',
        "averagedata"   :   True,
        "avgchannel"    :   '64',
        "coloraxis"     :   'field',
        "overwrite"     :   True,
},
    input = INPUT,
    output = OUTPUT,
    label = 'plot_amp_uvdist:: Plot amplitude vs distance')


# One final useful plot we will make is a datastream plot of the antenna2 in a baseline for the data versus ea01. This shows,
# assuming that ea01 is in the entire observation, when various antennas drop out.
recipe.add('cab/casa_plotms', 'antenna_dropout', {
        "vis"       :   MS,
        "plotfile"  :   MS + '-antenna_dropout.png',
        "xaxis"     :   'time',
        "yaxis"     :   'antenna2',
        "antenna"   :   REFANT,
        "selectdata":   True,
        "coloraxis" :   'field',
        "overwrite" :   True,
},
    input = INPUT,
    output = OUTPUT,
    label = "antenna_dropout:: Plot antenna dropout")


# As mentioned in the observing log above, antennas ea10, ea12, and ea22 do not have good baseline positions. Antenna ea10
# was not in the array, but, for the other two antennas, any improved baseline positions need to be incorporated. The
# importance of this step is that the visibility function is a function of u and v. If the baseline positions are incorrect,
# then u and v will be calculated incorrectly and there will be errors in the image. The calculations are inserted via gencal
# which, since CASA 3.4, allows automated lookup of the corrections
recipe.add('cab/casa_gencal', 'baseline_positions', {
        "vis"       :   MS,
        "caltable"  :   ANTPOS_TABLE,
        "caltype"   :   'antpos',
},
    input = INPUT,
    output = OUTPUT,
    label = 'baseline_positions:: Correct baseline positions')

# The next step is to provide a flux density value for the bandpass and flux calibrator J1331+3030 (a.k.a. 3C 286). Later, for the
# final step in determining the calibration solutions, we will use the calibrated gains of the different sources to transfer
# the flux density scaling to the gain (phase) calibrator (J219+4829). At this stage, we only set the flux density model and not 
#the polarization model for 3C 286; otherwise the early calibration
# steps would use the low signal-to-noise in the uncalibrated Stokes Q and U to provide poor calibration solutions.

recipe.add('cab/casa_setjy', 'set_flux_scaling', {
        "vis"           :   MS,
        "field"         :   BPCAL,
        "standard"      :   'Perley-Butler 2013',
        "model"         :   '3C286_L.im',
        "usescratch"    :   False,
        "scalebychan"   :   True,
        "spw"           :   '',
},
    input = INPUT,
    output = OUTPUT,
    label = 'set_flux_scaling:: Set flux density value for the amplitude calibrator')


#After setjy, we do an initial phase cal on the bandpass calibrator, to sort out phase variations prior to solving for bandpass itself.
#The channel range is chosen so that the gains obtained are good enough, this is the central region from a total channel number of 256. Need to check if RFI free.

recipe.add('cab/casa_gaincal', 'phase_cal', {
        "vis"           :   MS,
        "caltable"      :   GAINCAL_TABLE,
        "field"         :   BPCAL,
        "refant"        :   REFANT,
        "spw"           :   '0:100~150',
        "gaintype"      :   'G',
        "calmode"       :   'p',
        "solint"        :   'int',
        "minsnr"        :   5,
        "gaintable"     :   [ANTPOS_TABLE],
},
    input=INPUT,
    output=OUTPUT,
    label = 'phase_cal::Initial phase calibration')





# The first stage of bandpass calibration involves solving for the antenna-based delays which put a phase ramp versus
# frequency channel in each spectral window. The K gain type in gaincal solves for the relative delays of each
# antenna relative to the reference antenna (parameter refant), so be sure you pick one that is there for this entire scan
# and good. This is not a full global delay, but gives one value per spw per polarization. Channel range chosen to exclude 
#20 channels on either end of the band. Changing the field from GCAL to BPCAL, check if this makes sense. Apply both antenna position
#correction and initial phase correction.
recipe.add('cab/casa_gaincal', 'delay_cal', {
        "vis"       :   MS,
        "caltable"  :   DELAYCAL_TABLE,
        "field"     :   BPCAL,
        "refant"    :   REFANT,
#        "spw"       :   '0:21~235',
        "gaintype"  :   'K',
        "solint"    :   'inf',
        "combine"   :   'scan',
        "minsnr"    :   5,
        "gaintable" :   [ANTPOS_TABLE, GAINCAL_TABLE],
},
    input=INPUT,
    output=OUTPUT,
    label = 'delay_cal:: Delay calibration')


# All data with the VLA are taken in spectral line
# mode, even if the science that one is conducting is continuum, and therefore requires a bandpass solution to account for
# gain variations with frequency. Solving for the bandpass won't hurt for continuum data, and, for moderate or high dynamic
# range image, it is essential. To motivate the need for solving for the bandpass, consider Figure 7. It shows the right
# circularly polarized data (RR polarization) for the source J1331+3030, which will serve as the bandpass calibrator. The
# data are color coded by spectral window, and they are averaged over all baselines, as earlier plots from plotms indicated
# that the visibility data are nearly constant with baseline length. Ideally, the visibility data would be constant as a
# function of frequency as well. The variations with frequency are a reflection of the (slightly) different antenna
# bandpasses.
recipe.add('cab/casa_bandpass', 'bandpass_cal', {
        "vis"       :   MS,
        "caltable"  :   BPCAL_TABLE,
        "field"     :   BPCAL,
#        "spw"       :   '0:21~235',
        "refant"    :   REFANT,
        "solint"    :   'inf',
        "bandtype"  :   'B',
        "fillgaps" :  21,
        "gaintable" :   [ANTPOS_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE],
},
    input=INPUT,
    output=OUTPUT,
    label = 'bandpass_cal:: Bandpass calibration')


# display the bandpass solutions. Note that in the plotcal inputs below, the amplitudes are being displayed as a function of
# frequency channel. The parameter subplot=221 is used to display multiple plots per page (2 plots per page in the y
# direction and 2 in the x direction). The first two commands below show the amplitude solutions (one per each polarization)
# and the last two show the phase solutions (one per each polarization). Parameter iteration='antenna' is used to step
# through separate plots for each antenna.
recipe.add('cab/casa_plotcal', 'plot_bandpass_amp_R', {
        "caltable"  :   BPCAL_TABLE,
        "poln"      :   'R',
        "xaxis"     :   'chan',
        "yaxis"     :   'amp',
        "field"     :   BPCAL,
        "subplot"   :   221,
#        "iteration" :   'antenna',
        "figfile"   :   PREFIX+'-B0-R-amp.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_bandpass_amp_R:: Plot bandpass table. AMP, R')

recipe.add('cab/casa_plotcal', 'plot_bandpass_amp_L', {
        "caltable"  :   BPCAL_TABLE,
        "poln"      :   'L',
        "xaxis"     :   'chan',
        "yaxis"     :   'amp',
        "field"     :   BPCAL,
        "subplot"   :   221,
#        "iteration" :   'antenna',
        "figfile"   :   PREFIX+'-B0-L-amp.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_bandpass_amp_L:: Plot bandpass table. AMP, L')

recipe.add('cab/casa_plotcal', 'plot_bandpass_phase_R', {
        "caltable"  :   BPCAL_TABLE,
        "poln"      :   'R',
        "xaxis"     :   'chan',
        "yaxis"     :   'phase',
        "field"     :   BPCAL,
        "subplot"   :   221,
#        "iteration" :   'antenna',
        "figfile"   :   PREFIX+'-B0-R-phase.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_bandpass_phase_R:: Plot bandpass table. PHASE, R')


recipe.add('cab/casa_plotcal', 'plot_bandpass_phase_L', {
        "caltable"  :   BPCAL_TABLE,
        "poln"      :   'L',
        "xaxis"     :   'chan',
        "yaxis"     :   'phase',
        "field"     :   BPCAL,
        "subplot"   :   221,
#        "iteration" :   'antenna',
        "figfile"   :   PREFIX+'-B0-L-phase.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_bandpass_phase_L:: Plot bandpass table. PHASE, L')





# Gain calibration - amplitude and phase - first for BPCAL.
recipe.add('cab/casa_gaincal', 'gaincal_bp', {
        "vis"       :   MS,
        "caltable"  :   GAINCAL_TABLE2,
        "field"     :   BPCAL,
        "solint"    :   'inf',
        "refant"    :   REFANT,
#        "spw"       :   '0:21~235',
        "gaintype"  :   'G',
        "calmode"   :   'ap',
        "solnorm"   :   False,
        "gaintable" :   [ANTPOS_TABLE, DELAYCAL_TABLE,BPCAL_TABLE],
        "interp"    :   ['linear','linear','nearest'],
},
    input=INPUT,
    output=OUTPUT,
    label="gaincal_bp:: Gain calibration for bandpass field")



# Gain calibration - amplitude and phase - now for GCAL.
recipe.add('cab/casa_gaincal', 'gaincal_g', {
        "vis"       :   MS,
        "caltable"  :   GAINCAL_TABLE2,
        "field"     :   GCAL,
        "solint"    :   'inf',
        "refant"    :   REFANT,
#        "spw"       :   '0:21~235',
        "gaintype"  :   'G',
        "calmode"   :   'ap',
        "solnorm"   :   False,
        "gaintable" :   [ANTPOS_TABLE, DELAYCAL_TABLE,BPCAL_TABLE],
        "append"    :   True,
},
    input=INPUT,
    output=OUTPUT,
    label="gaincal_g:: Gain calibration for gain calibrator field")



# Plot gain cal solutions
recipe.add('cab/casa_plotcal', 'plot_gaincal_phase_R', {
        "caltable"  :   GAINCAL_TABLE2,
        "xaxis"     :   'time',
        "yaxis"     :   'phase',
        "poln"      :   'R',
        "plotrange" :   [-1,-1,-180,180],
        "figfile"   :   PREFIX+'-G1-phase-R.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_gaincal_phase_R:: Plot gain cal. PHASE, R')

recipe.add('cab/casa_plotcal', 'plot_gaincal_phase_L', {
        "caltable"  :   GAINCAL_TABLE2,
        "xaxis"     :   'time',
        "yaxis"     :   'phase',
        "poln"      :   'L',
        "plotrange" :   [-1,-1,-180,180],
        "figfile"   :   PREFIX+'-G1-phase-L.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_gaincal_phase_L:: Plot gain cal. PHASE, L')

recipe.add('cab/casa_plotcal', 'plot_gaincal_amp_R', {
        "caltable"  :   GAINCAL_TABLE2,
        "xaxis"     :   'time',
        "yaxis"     :   'amp',
        "poln"      :   'R',
        "figfile"   :   PREFIX+'-G1-AMP-R.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_gaincal_amp_R:: Plot gain cal. AMP, R')

recipe.add('cab/casa_plotcal', 'plot_gaincal_amp_L', {
        "caltable"  :   GAINCAL_TABLE2,
        "xaxis"     :   'time',
        "yaxis"     :   'amp',
        "poln"      :   'L',
        "figfile"   :   PREFIX+'-G1-amp-L.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_gaincal_amp_L:: Plot gain cal. AMP, L')




# Set fluxscale
recipe.add('cab/casa_fluxscale', 'fluxscale', {
        "vis"           :   MS,
        "caltable"      :   GAINCAL_TABLE2,
        "fluxtable"     :   FLUXSCALE_TABLE,
        "reference"     :   [BPCAL],
        "transfer"      :   [GCAL],
        "incremental"   :   False,
},
    input=INPUT,
    output=OUTPUT,
    label='fluxscale:: Set fluxscale')

#Plot fluxscale results
recipe.add('cab/casa_plotcal', 'plot_fluxscale_amp_R', {
        "caltable"  :   FLUXSCALE_TABLE,
        "xaxis"     :   'time',
        "yaxis"     :   'amp',
        "poln"      :   'R',
        "figfile"   :   PREFIX+'-FS-AMP-R.png',
},
    input=INPUT,
    output=OUTPUT,
    label='plot_flaxscale_amp_R:: Plot fluxscale AMP, R')



# Apply calibration to BPCAL
recipe.add('cab/casa_applycal', 'applycal_bp', {
        "vis"      :    MS,
        "field"     :   BPCAL,
        "gaintable" :   [ANTPOS_TABLE, DELAYCAL_TABLE,BPCAL_TABLE,FLUXSCALE_TABLE],
        "gainfield" :   ['','','',BPCAL],
        "interp"    :   ['','','','nearest'],
        "spw"       :   '0:21~235',
        "calwt"     :   [False],
        "parang"    :   False,
},
    input=INPUT,
    output=OUTPUT,
    label='applycal_bp:: Apply calibration to Bandpass Calibrator')

# Apply calibration to GCAL
recipe.add('cab/casa_applycal', 'applycal_g', {
        "vis"      :    MS,
        "field"     :   GCAL,
        "gaintable" :   [ANTPOS_TABLE, DELAYCAL_TABLE,BPCAL_TABLE,FLUXSCALE_TABLE],
        "gainfield" :   ['','','',GCAL],
        "interp"    :   ['','','','nearest'],
#        "spw"       :   '0:21~235',
        "calwt"     :   [False],
        "parang"    :   False,
},
    input=INPUT,
    output=OUTPUT,
    label='applycal_g:: Apply calibration to gain Calibrator')


# Apply calibration to TARGET
recipe.add('cab/casa_applycal', 'applycal_tar', {
        "vis"      :    MS,
        "field"     :   TARGET,
        "gaintable" :   [ANTPOS_TABLE, DELAYCAL_TABLE,BPCAL_TABLE,FLUXSCALE_TABLE],
        "gainfield" :   ['','','',BPCAL],
#        "spw"       :   '0:21~235',
        "interp"    :   ['','','','linear'],
        "calwt"     :   [False],
        "parang"    :   False,
},
    input=INPUT,
    output=OUTPUT,
    label='applycal_tar:: Apply calibration to target field')

recipe.add('cab/casa_plotms', 'plot_amp_phase', {
        "vis"           :   MS,
        "field"         :   BPCAL,
#        "spw"           :   '0:21~235',
        "correlation"   :   'RR',
        "timerange"     :   '',
        "antenna"       :   '',
        "xaxis"         :   'phase',
        "xdatacolumn"   :   'corrected',
        "yaxis"         :   'amp',
        "ydatacolumn"   :   'corrected',
        "coloraxis"     :   'corr',
        "plotfile"      :   PREFIX+'-fld1-corrected-ampvsphase.png',
        "overwrite"     :   True,
},
    input=INPUT,
    output=OUTPUT,
    label='plot_amp_phase:: Plot amplitude vs phase')


corr_ms = '12A-405.sb7601493.eb10633016.56086.127048738424-corr.ms'
recipe.add('cab/casa_split', 'split_corr_data',
    {
        "vis"       :   MS,
        "outputvis" :   corr_ms,
        "field"     :   str(TARGET),
        "datacolumn":   'corrected',
    },
    input=INPUT,
    output=OUTPUT,
    label='split_corr_data:: Split corrected data from MS')



MSCONTSUB = '12A-405.sb7601493.eb10633016.56086.127048738424.ms.contsub'
MS = corr_ms
# Fields
GCAL = '0'
TARGET = '1'
BPCAL = '2' # 3C286

# Reference antenna
REFANT = 'ea21'
SPW = '0:21~235'
# Calibration tables
LSM0 = PREFIX + '.lsm.html'
SELFCAL_TABLE1 = PREFIX + '.SF1:output'
IMAGE1= PREFIX+'image1:output'
MASK1=PREFIX+'mask1.fits'
IMAGE2=PREFIX+'image2:output'
nchans = 256
chans = [21,235]


## Clean-Mask-Clean 
imname0 = PREFIX+'image0'
maskname0 = PREFIX+'mask0.fits'
maskname01 = PREFIX+'mask01.fits'
imname1 = PREFIX+'image1'

recipe.add('cab/wsclean', 'image_target_field_r0', {
        "msname"        :   MS,
        "channelrange"  :   chans,               #Other channels don't have any data   
        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
        "npix"          :   1026,                   # Image size in pixels
        "trim"          :   1024,                    # To avoid aliasing
        "cellsize"      :   2.5,                      # Size of each square pixel
        "clean_iterations"  :   50000000,
        "auto-mask"     :   5,
        "mgain"         :   0.9,
        "local-rms"     :   True,
        "auto-threshold":   1,
        "channelsout"   :   4,
        "datacolumn"    :   "DATA",
        "prefix"        :   '%s:output' %(imname0),
},
    input=INPUT,
    output=OUTPUT,
    label="image_target_field_r0:: Image target field first round")

# Diversity is a good thing... lets add some DDFacet to this soup bowl
imname=PREFIX+'ddfacet'
recipe.add("cab/ddfacet", "ddfacet_test",
            {
                "Data-MS": [MS],
                "Output-Name": imname,
                "Image-NPix": 1024,
                "Image-Cell": 2,
                "Cache-Reset": True,
                "Freq-NBand": 2,
                "Weight-ColName": "WEIGHT",
                "Beam-Model": "FITS",
                "Beam-FITSFile": "'beams/JVLA-L-centred-$(xy)_$(reim).fits'",
                "Data-ChunkHours": 0.5,
                "Data-Sort": True,
		"Log-Boring": True,
		"Deconv-MaxMajorIter": 1,
		"Deconv-MaxMinorIter": 10,
            },
            input=INPUT, output=OUTPUT, shared_memory="36gb",
            label="image_target_field_r0ddfacet:: Make a test image using ddfacet")

lsm0=PREFIX+'-LSM0'
#Source finding for initial model
recipe.add("cab/pybdsm", "extract_init_model", {
           "image"             :  '%s-MFS-image.fits:output' %(imname0),
           "outfile"           :  '%s:output'%(lsm0),
           "thresh_pix"        :  15,
           "thresh_isl"        :  10,
           "port2tigger"       :  True,
},
           input=INPUT, output=OUTPUT,
           label="extract_init_model:: Make initial model from preselfcal image")


# Copy CORRECTED_DATA to DATA, so we can start selfcal
recipe.add("cab/msutils", "move_corrdata_to_data", {
            "command"           : "copycol",
            "msname"            : MS,
            "fromcol"           : "CORRECTED_DATA",
            "tocol"             : "DATA",
},
        input=INPUT, output=OUTPUT,
        label="move_corrdata_to_data::msutils")


#Add bitflag column. To keep track of flagsets. 
recipe.add("cab/msutils", "msutils", {
        'command'    : 'prep',
        'msname'     : MS,
},
    input=INPUT, output=OUTPUT,
    label="prepms::Adds flagsets")


#First selfcal round
recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm0", {
           "skymodel"           : "%s.lsm.html:output"%(lsm0),
           "msname"             : MS,
           "threads"            : 16,
           "column"             : "DATA",
           "output-data"        : "CORR_DATA",
           "Gjones"             : True,
           "Gjones-solution-intervals" : [20,64],     #Ad-hoc right now, subject to change
           "Gjones-matrix-type" : "GainDiagPhase",
           "write-flags-to-ms"  :  True,
           "write-flagset"      : "stefcal",
           "read-legacy-flags"  : True,
           "read-flags-from-ms" : True,
           "read-flagsets"       : "-stefcal",    # ignore any stefcal flags that may exist
           "Gjones-ampl-clipping"  :   True,
           "Gjones-ampl-clipping-low"  :   0.15,
           "Gjones-ampl-clipping-high" :   2.0,
           "Gjones-thresh-sigma" :  10,
           "Gjones-chisq-clipping" : False,
           "make-plots"         : True,
           "tile-size"          : 512,
},
           input=INPUT, output=OUTPUT,
           label="calibrator_Gjones_subtract_lsm0:: Calibrate and subtract LSM0")

imname2 = PREFIX+"image2"

recipe.add('cab/wsclean', 'image_target_field_r2', {
        "msname"        :   MS,
        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
        "npix"          :   1026,                   # Image size in pixels
        "trim"          :   1024,                    # To avoid aliasing
        "cellsize"      :   3,                      # Size of each square pixel
        "clean_iterations"  :   100,
        "auto-mask"         :   3,
        "local-rms"         :   True,
        "auto-threshold"    :   0.5,                      #Since it is not masked
        "stokes"            :   "I",
        "channelrange"      :   chans,
        "channelsout"       :   2,
        "mgain"             :   0.95,
        "prefix"            :   "%s:output"%(imname2),
},
        input=INPUT, output=OUTPUT,
        label="image_target_field2::Image the target field after selfcal1"
)


#Second selfcal round, amp+phase
recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm1", {
           "skymodel"           : "%s.lsm.html:output"%(lsm0),
           "add-vis-model"      : True,    # add clean components to first model
           "msname"             : MS,
           "threads"            : 16,
           "column"             : "DATA",
           "output-data"        : "CORR_RES",
           "Gjones"             : True,
           "Gjones-solution-intervals" : [20,64],     #Ad-hoc right now, subject to change
           "Gjones-matrix-type" : "GainDiagPhase",
           "read-flagsets"      : "-stefcal",
           "write-flags-to-ms"  : True,
           "write-flagset"      : "stefcal",
           "write-flagset-policy" : "replace",
           "read-legacy-flags"  : True,
           "read-flags-from-ms" : True,
           "Gjones-ampl-clipping"  :   True,
           "Gjones-ampl-clipping-low"  :   0.15,
           "Gjones-ampl-clipping-high"  :   2.0,
           "Gjones-thresh-sigma" :  8,
           "Gjones-chisq-clipping" : True,
           "Ejones"    : True,
           "beam-files-pattern" : "beams/JVLA-L-centred-$(corr)_$(reim).fits", #some beam into the mix
           "beam-type"   : "fits",
           "beam-l-axis" : "-X",
           "beam-m-axis" : "Y",
           "tile-size"          : 512,
           "make-plots"         : True,
           "save-config"        : "selfcal_2nd_round",
},
           input=INPUT, output=OUTPUT,
           label="calibrator_Gjones_subtract_lsm0_cc:: Calibrate and subtract LSM0 and clean components")


imname3 = PREFIX+"image3"
recipe.add('cab/wsclean', 'image_target_field_r3', {
        "msname"            :   MS,
        "weight"            :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
        "npix"              :   512,                   # Image size in pixels
        "trim"              :   512,                    # To avoid aliasing
        "cellsize"          :   1,                      # Size of each square pixel
        "clean_iterations"  :   50,
        "auto-mask"         :   3,
#        "local-rms"        :   True,
        "nomfsweighting"    :   True,
        "auto-threshold"    :   0.5,
        "mgain"             :   0.95,
        "channelsout"       :   _nchans,
        "stokes"            :   "I",
#        "channelrange"      :   chans,
        "prefix"            :   "%s:output"%(imname3),
},
        input=INPUT, output=OUTPUT,
        label="image_target_field3::Image the target field after selfcal2")


combprefix = imname3
imagelist = ['{0:s}-{1:04d}-image.fits:output'.format(combprefix, jj) for jj in range(_nchans)]

recipe.add('cab/fitstool', 'stack_channels',
            {
                 "stack"      :   True,
                 "image"      :   imagelist,
                 "fits-axis"  :   'FREQ',
                 "output"     :   '{:s}-cube.dirty.fits'.format(combprefix),
            },
            input=INPUT,
            output=OUTPUT,
            label='stack_channels:: Stack individual channels made by WSClean')

##################################################################
# Make cube of the remaining residues and see if there is some
# interresting HI stuff in there
# Use lwimager just for the sake of diversity
##################################################################
imname4 = PREFIX+"image4"
recipe.add('cab/lwimager', 'lwimager_residue_cube', {
        "msname"            : MS,
        "column"            : "CORRECTED_DATA",
        "weight"            : "briggs",
        "robust"            : 0.0,
        "npix"              : 256,
        "padding"           : 2.0,
        "cellsize"          : 1.000,
        "nchan"             : _nchans,
        "chanstart"         : 0,
        "chanstep"          : 1,
        "img_nchan"         : _nchans,
        "img_chanstart"     : 0,
        "img_chanstep"      : 1,
        "niter"             : 10,
        "gain"              : 0.8,
        "sigma"             : 0.5,
        "prefix"            : imname4,
        "stokes"            : "I",
        "mode"              : "velocity"
},
    input=OUTPUT,
    output=OUTPUT,
    label='lwimager_residue_cube:: make a cube after most of the continuum has'
          ' been cleaned and subtracted away')



# Run Sofia
recipe.add('cab/sofia', 'sofia',
            {
        #    USE THIS FOR THE WSCLEAN DIRTY CUBE
        #    "import.inFile"     :   '{:s}-cube.dirty.fits:output'.format(combprefix),
        #    USE THIS FOR THE CASA CLEAN CUBE
	    "import.inFile"         :   '{:s}-cube.dirty.fits:output'.format(combprefix),       # CASA CLEAN cube
            "steps.doMerge"         :   True,
            "steps.doMom0"          :   True,
            "steps.doMom1"          :   False,
            "steps.doParameterise"  :   False,
            "steps.doReliability"   :   False,
            "steps.doWriteCat"      :   False,
            "steps.doWriteMask"     :   True,
            "steps.doFlag"          :   True,
           # "flag.regions"          :   sf_flagregion,
            "SCfind.threshold"      :   4,
            "merge.radiusX"         :   2,
            "merge.radiusY"         :   2,
            "merge.radiusZ"         :   3,
            "merge.minSizeX"        :   3,
            "merge.minSizeY"        :   3,
            "merge.minSizeZ"        :   5,
            },
            input=INPUT,
            output=OUTPUT,
            label='sofia:: Make SoFiA mask and images')




recipe.run([
   "quack_flagging",
   "autocorr_flagging",
   "antenna_flagging",
   "badchan_flagging",
   "aoflag_data",
   "plot_manual",
   "plot_amp_uvdist",
   "antenna_dropout",
   "baseline_positions",
   "set_flux_scaling",
   "phase_cal",
   "delay_cal",
   "bandpass_cal",
   "plot_bandpass_amp_R",
   "plot_bandpass_amp_L",
   "plot_bandpass_phase_R",
   "plot_bandpass_phase_L",
   "gaincal_bp",
   "gaincal_g",
   "plot_gaincal_phase_R",
   "plot_gaincal_phase_L",
   "plot_gaincal_amp_R",
   "plot_gaincal_amp_L",
   "fluxscale",
   "plot_flaxscale_amp_R",
   "applycal_bp",
   "applycal_g",
   "applycal_tar",
   "plot_amp_phase",
   "split_corr_data",
   'prepms',
   'image_target_field_r0',
   'image_target_field_r0ddfacet',
   'extract_init_model',
   'calibrator_Gjones_subtract_lsm0',
   'image_target_field2',
   'calibrator_Gjones_subtract_lsm0_cc',
   'image_target_field3',
   'stack_channels',
   'lwimager_residue_cube',
#   'sofia',
], resume=False)
