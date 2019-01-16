import stimela
import os
import unittest
import subprocess

class ngc417_reduce(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
                unittest.TestCase.setUpClass()
                #I/O
                global INPUT
                INPUT = 'input'
                global MSDIR
                MSDIR = 'msdir'

                global MS
                MS = '12A-405.sb7601493.eb10633016.56086.127048738424.ms'
                global PREFIX
                PREFIX = 'vla_NGC417_LBand'


                # Fields
                global GCAL
                GCAL = '0'
                global TARGET
                TARGET = '1'
                global BPCAL
                BPCAL = '2' # 3C286

                # Reference antenna
                global REFANT
                REFANT = 'ea21'

                # Calibration tables
                global ANTPOS_TABLE
                ANTPOS_TABLE = PREFIX + '.antpos:output'
                global BPCAL_TABLE
                BPCAL_TABLE = PREFIX + '.B0:output'
                global DELAYCAL_TABLE
                DELAYCAL_TABLE = PREFIX + '.K0:output'
                global GAINCAL_TABLE
                GAINCAL_TABLE = PREFIX + '.G0:output'
                global FLUXSCALE_TABLE
                FLUXSCALE_TABLE = PREFIX + '.fluxscale:output'
                global GAINCAL_TABLE2
                GAINCAL_TABLE2 = PREFIX + '.G1:output'
                global _nchans
                _nchans = 32

                global LABEL
                LABEL = "ngc147_reduction"
                global OUTPUT
                OUTPUT = "output_%s" % LABEL
                global MSCONTSUB
                MSCONTSUB = '12A-405.sb7601493.eb10633016.56086.127048738424.ms.contsub'
                

                global SPW
                SPW = '0:21~235'
                # Calibration tables
                global LSM0
                LSM0 = PREFIX + '.lsm.html'
                global SELFCAL_TABLE1
                SELFCAL_TABLE1 = PREFIX + '.SF1:output'
                global IMAGE1
                IMAGE1= PREFIX+'image1:output'
                global MASK1
                MASK1=PREFIX+'mask1.fits'
                global IMAGE2
                IMAGE2=PREFIX+'image2:output'
                global nchans
                nchans = 256
                global chans
                chans = [21,235]

                ## Clean-Mask-Clean 
                global imname0
                imname0 = PREFIX+'image0'
                global maskname0
                maskname0 = PREFIX+'mask0.fits'
                global maskname01
                maskname01 = PREFIX+'mask01.fits'
                global imname1
                imname1 = PREFIX+'image1'
                global corr_ms
                corr_ms = '12A-405.sb7601493.eb10633016.56086.127048738424-corr.ms'
                global lsm0
                lsm0=PREFIX+'-LSM0'
                stimela.register_globals()

        @classmethod
        def tearDownClass(cls):
                unittest.TestCase.tearDownClass()

        def tearDown(self):
                unittest.TestCase.tearDown(self)

        def setUp(self):
                unittest.TestCase.setUp(self)

        def testEndToEndReduction(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                
                recipe = stimela.Recipe('VLA NGC417 reduction script', ms_dir=MSDIR)


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
                input=OUTPUT,
                output=OUTPUT,
                label='plot_amp_phase:: Plot amplitude vs phase')


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
                        ])

                recipe = stimela.Recipe('VLA NGC417 reduction script', ms_dir=MSDIR)
                # Copy CORRECTED_DATA to DATA, so we can start uv_contsub
                recipe.add("cab/msutils", "move_corrdata_to_data", {
                        "command"           : "copycol",
                        "msname"            : MS,
                        "fromcol"           : "CORRECTED_DATA",
                        "tocol"             : "DATA",
                },
                        input=INPUT, output=OUTPUT,
                        label="move_corrdata_to_data::msutils")

                recipe.add('cab/casa_split', 'split_corr_data',
                {
                        "vis"       :   MS,
                        "outputvis" :   MS[:-3]+'-corr.ms',
                        "field"     :   str(TARGET),
                        "datacolumn":   'data',
                },
                input=INPUT,
                output=OUTPUT,
                label='split_corr_data:: Split corrected data from MS')

                MS = MS[:-3]+'-corr.ms'

                recipe.add('cab/casa_clearcal', 'prep_split_data',
                {
                        "vis"       :   MS,
                        "addmodel"  :   True
                },
                input=INPUT,
                output=OUTPUT,
                label='prep_split_data:: Prep split data with casa clearcal')

                ## Clean-Mask-Clean 
                imname0=PREFIX+'image0'
                maskname0=PREFIX+'mask0.fits'
                maskname01=PREFIX+'mask01.fits'
                imname1=PREFIX+'image1'

                recipe.add('cab/wsclean', 'image_target_field_r0', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "channelrange"  :   [21,235],               #Other channels don't have any data   
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   5000000,
                #        "stokes"    : "I",
                        "mgain"         :   0.9,
                        "auto-threshold":   5,                      #Shallow clean
                        "prefix"        :   '%s:output' %(imname0),

                
                },
                input=INPUT,
                output=OUTPUT,
                label="image_target_field_r0:: Image target field first round")

                recipe.add('cab/cleanmask', 'mask0', {
                "image"  : '%s-image.fits:output' %(imname0),
                "output" : '%s:output' %(maskname0),
                "dilate" : False,
                "sigma"  : 20,
                },
                input=INPUT,
                output=OUTPUT,
                label='mask0:: Make mask')
                

                recipe.add('cab/wsclean', 'image_target_field_r1', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "channelrange"  :   [21,235],               #Other channels don't have any data   
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   5000000,
                        "mgain"         :   0.9,
                        "stokes"    : "I",
                        "fitsmask"      :   '%s:output' %(maskname0),
                        "auto-threshold":   1,                      #Since it is masked
                        "prefix"        :   '%s:output' %(imname1),


                },
                input=INPUT,
                output=OUTPUT,
                label="image_target_field_r1:: Image target field second round")

                recipe.add('cab/cleanmask', 'mask01', {
                "image"  : '%s-image.fits:output' %(imname1),
                "output" : '%s:output' %(maskname01),
                "dilate" : False,
                "sigma"  : 15,
                },
                input=INPUT,
                output=OUTPUT,
                label='mask01:: Make mask')


                ## Cube switched off for now. ##REMEBER TO CHANGE THRESHOLD TO AUTO THRESHOLD AND MGAIN VALUE.##

                recipe.add('cab/wsclean', 'cube_target_field', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "channelrange"  :   [21,235],
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500000,
                        "mgain"         : 0.1,
                        "stokes"    : "I",
                        "channelsout"   : 10,
                        "threshold"     : 0.0001,
                        "prefix"        : "pre-self-cal-cube"+LABEL,
                
                },
                input=INPUT,
                output=OUTPUT,
                label="cube_target_field:: Image cube for target field")

                lsm0=PREFIX+'-LSM0'
                #Source finding for initial model
                recipe.add("cab/pybdsm", "extract_init_model", {
                        "image"             :  '%s-image.fits:output' %(imname1),
                        "outfile"           :  '%s:output'%(lsm0),
                        "thresh_pix"        :  25,
                        "thresh_isl"        :  15,
                        "port2tigger"       :  True,
                },
                        input=INPUT, output=OUTPUT,
                        label="extract_init_model:: Make initial model from preselfcal image")

                #Add bitflag column. To keep track of flagsets. 
                recipe.add("cab/msutils", "msutils", {
                        'command'    : 'prep',
                        'msname'     : MS,
                },
                input=INPUT, output=OUTPUT,
                label="prepms::Adds flagsets")

                #Not used currently.
                recipe.add("cab/flagms", "backup_initial_flags", {
                        "msname"        : MS,
                        "flagged-any"   : "legacy+L",
                        "flag"          : "legacy",
                },
                        input=INPUT, output=OUTPUT,
                        label="backup_initial_flags:: Backup selfcal flags")

                #First selfcal round
                recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm0", {
                        "skymodel"           : "%s.lsm.html:output"%(lsm0),
                        "msname"             : MS,
                        "threads"            : 16,
                        "column"             : "DATA",
                        "output-data"        : "CORR_RES",
                        "Gjones"             : True,
                        "Gjones-solution-intervals" : [20,0],     #Ad-hoc right now, subject to change
                        "Gjones-matrix-type" : "GainDiagPhase",
                #           "DDjones-smoothing-intervals" : 1,
                #           "Gjones-ampl-clipping"  :   True,
                #           "Gjones-ampl-clipping-low"  :   0.15,
                #           "Gjones-ampl-clipping-high"  :   3.5,
                #           "Gjones-thresh-sigma" :  5,
                #           "Gjones-chisq-clipping" : False,
                #           "make-plots"         : True,
                        "tile-size"          : 512,
                        "field-id"           : int(TARGET),
                },
                        input=INPUT, output=OUTPUT,
                        label="calibrator_Gjones_subtract_lsm0:: Calibrate and subtract LSM0")

                imname2 = PREFIX+"image2"

                recipe.add('cab/wsclean', 'image_target_field_r2', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500000,
                        "stokes"    : "I",
                        "mgain"         : 0.9,
                        "auto-threshold":   5,                      #Since it is not masked
                        "prefix"        : "%s:output"%(imname2),
                },
                        input=INPUT, output=OUTPUT,
                        label="image_target_field2::Image the target field after selfcal1"
                )

                # Diversity is a good thing... lets add some DDFacet to this soup bowl
                imname=PREFIX+'ddfacet'
                recipe.add("cab/ddfacet", "ddfacet_test",
                        {
                                "Data-MS": [MS],
                                "Output-Name": imname,
                                "Image-NPix": 2048,
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
                                "Deconv-MaxMinorIter": 500,
                        },
                        input=INPUT, output=OUTPUT, shared_memory="36gb",
                        label="image_target_field_r0ddfacet:: Make a test image using ddfacet")

                #Get a better image by cleaning with masks, two rounds. Noise in the earlier 
                #image around 60 microJy.
                maskname1=PREFIX+"mask1.fits"
                recipe.add('cab/cleanmask', 'mask1', {
                #    "image"  : "pre-self-cal--image.fits:output",
                "image"  : '%s-image.fits:output' %(imname2),
                "output" : '%s:output' %(maskname1),
                "dilate" : False,
                "sigma"  : 10,      #lower thresh to pick us more sources.
                },
                input=INPUT,
                output=OUTPUT,
                label='mask1:: Make mask on selfcal image')



                imname3=PREFIX+"-image3"
                recipe.add('cab/wsclean', 'image_target_field3', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500000,
                        "mgain"         : 0.9,
                        "stokes"    : "I",
                        "auto-threshold"     : 1,
                        "prefix"        : '%s:output' %(imname3),
                        "fitsmask"      : '%s:output' %(maskname1),
                },
                        input=INPUT, output=OUTPUT,
                        label="image_target_field3::Image the target field after selfcal1 with masks"
                )

                lsm1=PREFIX+'-LSM1'

                #Run pybdsm on the new image. Do amplitude and phase selfcal. 
                recipe.add("cab/pybdsm", "extract_pselfcal_model", {
                        "image"             :  '%s-image.fits:output' %(imname3),
                        "outfile"           :  '%s:output'%(lsm1),
                        "thresh_pix"        :  10,
                        "thresh_isl"        :  5,
                        "port2tigger"       :  True,
                        "clobber"           : True,
                },
                        input=OUTPUT, output=OUTPUT,
                        label="extract_pselfcal_model:: Make new model from selfcal image")

                recipe.add("cab/flagms", "unflag_pselfcalflags", {
                        "msname"             : MS,
                        "unflag"             : "FLAG0",
                },
                        input=INPUT, output=OUTPUT,
                        label="unflag_pselfcalflags:: Unflag phase selfcal flags")

                #Stitch LSMs together
                lsm2=PREFIX+'-LSM2'
                recipe.add("cab/tigger_convert", "stitch_lsms1", {
                        "input-skymodel" :   "%s.lsm.html:output" % lsm0,
                        "output-skymodel" :   "%s.lsm.html:output" % lsm2,
                        "append" :   "%s.lsm.html:output" % lsm1,
                        "force"  : True,
                },
                        input=INPUT, output=OUTPUT,
                        label="stitch_lsms1::Create master lsm file")



                #Second selfcal round
                recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm1", {
                        "skymodel"           : "%s.lsm.html:output"%(lsm2),
                        "msname"             : MS,
                        "threads"            : 16,
                        "column"             : "DATA",
                        "output-data"        : "CORR_RES",
                        "Gjones"             : True,
                        "Gjones-solution-intervals" : [20,0],     #Ad-hoc right now, subject to change
                        "Gjones-matrix-type" : "GainDiagPhase",
                        # "Gjones-smoothing-intervals" : [4,4],
                        # "Gjones-ampl-clipping"  :   True,
                        # "Gjones-ampl-clipping-low"  :   0.15,
                        # "Gjones-ampl-clipping-high"  :   1.5,
                        # "Gjones-thresh-sigma" :  5,
                        # "Gjones-chisq-clipping" : True,
                        "tile-size"          : 512,
                        # "make-plots"         : True,
                        "field-id"           : int(TARGET),
                        "save-config"        : "selfcal_2nd_round",
                },
                        input=INPUT, output=OUTPUT,
                        label="calibrator_Gjones_subtract_lsm1:: Calibrate and subtract LSM1")


                imname4 = PREFIX+"image4"

                recipe.add('cab/wsclean', 'image_target_field_r4', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "datacolumn"   :   "CORRECTED_DATA",
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500000,
                        "mgain"         : 0.9,
                        "stokes"    : "I",
                        "auto-threshold"     : 3,
                        "prefix"        : "%s:output"%(imname4),
                },
                        input=INPUT, output=OUTPUT,
                        label="image_target_field4::Image the target field after selfcal2"
                )


                maskname2=PREFIX+"mask2.fits"
                recipe.add('cab/cleanmask', 'mask2', {
                #    "image"  : "pre-self-cal--image.fits:output",
                "image"  : '%s-image.fits:output' %(imname4),
                "output" : '%s:output' %(maskname2),
                "no-negative" : True,
                "dilate" : True,
                "sigma"  : 5,      #lower thresh to pick us more sources.
                },
                input=INPUT,
                output=OUTPUT,
                label='mask2:: Make mask on second selfcal image')





                imname5 = PREFIX+"image5"
                recipe.add('cab/wsclean', 'image_target_field_r5', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                        "datacolumn"   :   "CORRECTED_DATA",
                        "weight"        :   "briggs 0",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500000,
                        "mgain"         : 0.9,
                        "stokes"    : "I",
                        "auto-threshold"     : 1,
                        "fitsmask"      :   '%s:output' %(maskname2),
                        "prefix"        : "%s:output"%(imname5),
                },
                        input=INPUT, output=OUTPUT,
                        label="image_target_field_r5::Image the target field after selfcal2"
                )



                #Run pybdsm on the new image. Do amplitude and phase selfcal. 
                recipe.add("cab/pybdsm", "extract_final_model", {
                        "image"             :  '%s-image.fits:output' %(imname3),
                        "outfile"           :  '%s:output'%(lsm1),
                        "thresh_pix"        :  10,
                        "thresh_isl"        :  5,
                        "port2tigger"       :  True,
                        "clobber"           : True,
                },
                        input=OUTPUT, output=OUTPUT,
                        label="extract_pselfcal_model:: Make new model from selfcal image")






                recipe.add('cab/wsclean', 'cube_target_field2', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                #        "channelrange"  :   [21,235],
                        "weight"        :   "natural",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   4696,                   # Image size in pixels
                        "trim"          :   4084,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500000,
                        "mgain"         : 0.9,
                        "stokes"    : "I",
                #        "nwlayers"  : 128,
                        "channelsout"   : 256,
                        "auto-threshold"     : 3,
                #        "multiscale"    : True,
                        "prefix"        : "post-uvsubcont-cube"+LABEL,

                },
                input=INPUT,
                output=OUTPUT,
                label="cube_target_field2:: Image cube for target field after selfcal")

                recipe.add('cab/casa_uvcontsub','uvcontsub',
                        {
                                "msname"         :    MS,
                                "field"          :    TARGET,
                                "fitorder"       :    1,
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label='uvcontsub:: Subtract continuum in the UV plane')


                #Image HI
                recipe.add('cab/casa_clean', 'casa_dirty_cube',
                        {
                                "msname"         :    MSCONTSUB,
                                "prefix"         :    PREFIX,
                #                 "field"          :    TARGET,
                #                 "column"         :    "CORRECTED_DATA",
                                "mode"           :    'channel',
                                "nchan"          :    nchans,
                                "interpolation"  :    'nearest',
                                "niter"          :    0,
                                "psfmode"        :    'hogbom',
                                "threshold"      :    '1mJy',
                                "npix"           :    1024,
                                "cellsize"       :    1,
                                "weight"         :    'natural',
                        #  "wprojplanes"    :    1,
                                "port2fits"      :    True,
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label='casa_dirty_cube:: Make a dirty cube with CASA CLEAN')

                
                #Instead, make wsclean dirty cube
                recipe.add('cab/wsclean', 'cube_target_field_dirty', {
                        "msname"        :   MS,
                        "field"         :   TARGET,
                #        "channelrange"  :   [21,235],
                        "weight"        :   "natural",               # Use Briggs weighting to weigh visibilities for imaging
                        "npix"          :   700,                   # Image size in pixels
                        "trim"          :   512,                    # To avoid aliasing
                        "cellsize"      :   1,                      # Size of each square pixel
                        "clean_iterations"  :   500,
                        "mgain"         : 0.9,
                        "stokes"    : "I",
                        "channelsout"   : nchans,
                        "niter"         : 0,
                        "threshold"     : 0.0001,
                        "prefix"        : "post-uvsubcont-cube"+LABEL,

                },
                input=INPUT,
                output=OUTPUT,
                label="cube_target_field_dirty:: Make dirty cube for target field")

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
                        "padding"           : 0.5,
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
                        "move_corrdata_to_data",
                        "split_corr_data",
                        "prep_split_data"
                        "image_target_field_r0",
                        "mask0", 
                        "image_target_field_r1",
                        "cube_target_field",
                        "extract_init_model",
                        "mask01",
                        "prepms",
                        "backup_initial_flags",
                        "calibrator_Gjones_subtract_lsm0",
                        "image_target_field2",
                        "mask1",
                        "image_target_field3",
                        "extract_pselfcal_model",
                        "unflag_pselfcalflags",
                        "stitch_lsms1",
                        "calibrator_Gjones_subtract_lsm1", 
                        "image_target_field4",    
                        "mask2",
                        "image_target_field_r5",
                        "cube_target_field2",
                        "uvcontsub",
                        "casa_dirty_cube",
                        "cube_target_field_dirty",
                        "lwimager_residue_cube",
                        "stack_channels",
                        "sofia"
                        ])