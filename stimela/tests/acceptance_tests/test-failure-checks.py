import stimela
import os
import unittest
import subprocess
from nose.tools import timed
import stimela.utils as stimela_utils
from stimela.recipe import PipelineException
class failure_checks(unittest.TestCase):
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
                os.mkdir(os.path.join(MSDIR, MS)) # make dummy
                global PREFIX
                PREFIX = 'error_tests'


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
                LABEL = "failure_checks"
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
                if not "SINGULARITY_PULLFOLDER" in os.environ:
                    raise ValueError("ENV SINGULARITY_PULLFOLDER not set! This test requires singularity images to be pulled")

        @classmethod
        def tearDownClass(cls):
                unittest.TestCase.tearDownClass()
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                os.rmdir(os.path.join(MSDIR, MS)) # make dummy
        def tearDown(self):
                unittest.TestCase.tearDown(self)

        def setUp(self):
                unittest.TestCase.setUp(self)
                
        def testFailCasaFlagdata(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('QUICK_FLAG_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_flagdata', 'quack_flagging', {
                                "vis"           :   MS,
                                "mode"         :   'manual',
                                "quackinterval" :   10.0,
                                "quackmode"     :   'beg',
                        },
                        input = INPUT,
                        output = OUTPUT,
                        label = 'quack_flagging:: Quack flagging',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailAutoflagger(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('AUTOFLAG_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/autoflagger', 'aoflag_data', {
                                "msname"    :   MS,
                                "column"    :   "DATA5",
                        },    
                        input=INPUT,
                        output=OUTPUT,    
                        label='aoflag_data:: Flag DATA column',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailPlotMS(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('PLOTMS_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_plotms', 'plot_manual', {
                                "vis"           :   MS,
                                "plotfile"      :   PREFIX + 'after_manual_flags.png',
                                "selectdata"    :    True,
                                "correlation"   :   'RR,LL',
                                "averagedata"   :   True,
                                "avgchannel"    :   '64',
                                "coloraxis"     :   'f1i2e3l4d5',
                                "overwrite"     :   True,
                        },
                        input = INPUT,
                        output = OUTPUT,
                        label = 'plot_manual:: Plot data after manual flagging',
                        time_out=300) 
                        recipe.run(resume=False)

        def testFailPlotMSSingularity(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('PLOTMS_SINGULARITY_FAIL', ms_dir=MSDIR, singularity_image_dir=os.environ["SINGULARITY_PULLFOLDER"])
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_plotms', 'plot_manual', {
                                "vis"           :   MS,
                                "plotfile"      :   PREFIX + 'after_manual_flags.png',
                                "selectdata"    :    True,
                                "correlation"   :   'RR,LL',
                                "averagedata"   :   True,
                                "avgchannel"    :   '64',
                                "coloraxis"     :   'f1i2e3l4d5',
                                "overwrite"     :   True,
                        },
                        input = INPUT,
                        output = OUTPUT,
                        label = 'plot_manual:: Plot data after manual flagging',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailGenCal(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('GENCAL_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_gencal', 'baseline_positions', {
                                "vis"       :   MS,
                                "caltable"  :   ANTPOS_TABLE,
                                "caltype"   :   'antpos',
                        },
                        input = INPUT,
                        output = OUTPUT,
                        label = 'baseline_positions:: Correct baseline positions',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailSetJy(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('SETJY_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_setjy', 'set_flux_scaling', {
                                "vis"           :   MS,
                                "field"         :   BPCAL,
                                "standard"      :   'Perley-Butler 2010',
                                "model"         :   '3C286_L.im',
                                "usescratch"    :   False,
                                "scalebychan"   :   True,
                                "spw"           :   '',
                        },
                        input = INPUT,
                        output = OUTPUT,
                        label = 'set_flux_scaling:: Set flux density value for the amplitude calibrator',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailGainCal(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('GAINCAL_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_gaincal', 'phase_cal', {
                                "vis"           :   MS,
                                "caltable"      :   GAINCAL_TABLE,
                                "field"         :   "BLABLABLA",
                                "refant"        :   "DORAYME",
                                "spw"           :   '0asdwe:1asd0egdfh0~1sad50as',
                                "gaintype"      :   'G',
                                "calmode"       :   'p',
                                "solint"        :   'int',
                                "minsnr"        :   5,
                                "gaintable"     :   [ANTPOS_TABLE],
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label = 'phase_cal::Initial phase calibration',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailBandpassCal(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('BANDPASS_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_bandpass', 'bandpass_cal', {
                                "vis"       :   MS,
                                "caltable"  :   BPCAL_TABLE,
                                "field"     :   BPCAL,
                        #        "spw"       :   '0:21~235',
                                "refant"    :   'DORAYME',
                                "solint"    :   'inf',
                                "bandtype"  :   'B',
                                "fillgaps" :  21,
                                "gaintable" :   [ANTPOS_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE],
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label = 'bandpass_cal:: Bandpass calibration',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailPlotcal(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('PLOTCAL_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_plotcal', 'plot_bandpass_amp_R', {
                                "caltable"  :   BPCAL_TABLE,
                                "poln"      :   'R',
                                "xaxis"     :   'chan',
                                "yaxis"     :   'amp',
                                "field"     :   "YADADIDA",
                                "subplot"   :   221,
                        #        "iteration" :   'antenna',
                                "figfile"   :   PREFIX+'-B0-R-amp.png',
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label='plot_bandpass_amp_R:: Plot bandpass table. AMP, R',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailFluxscale(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('FLUXSCALE_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_fluxscale', 'fluxscale', {
                                "vis"           :   MS,
                                "caltable"      :   GAINCAL_TABLE2,
                                "fluxtable"     :   FLUXSCALE_TABLE,
                                "reference"     :   ["dadado"],
                                "transfer"      :   ["helloworld"],
                                "incremental"   :   False,
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label='fluxscale:: Set fluxscale',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailApplyCal(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('APPLYCAL_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_applycal', 'applycal_bp', {
                                "vis"      :    MS,
                                "field"     :   BPCAL,
                                "gaintable" :   [ANTPOS_TABLE, DELAYCAL_TABLE,BPCAL_TABLE,FLUXSCALE_TABLE],
                                "gainfield" :   ['','','',BPCAL],
                                "interp"    :   ['','','','nearest'],
                                "spw"       :   '0:2a1~2dw3s5',
                                "calwt"     :   [False],
                                "parang"    :   False,
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label='applycal_bp:: Apply calibration to Bandpass Calibrator',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailSplit(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('SPLIT_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add('cab/casa_split', 'split_corr_data',
                        {
                                "vis"       :   MS,
                                "outputvis" :   corr_ms + ".dadado.ms",
                                "field"     :   str(TARGET),
                                "datacolumn":   'corrected',
                                "spw"       :   '0:a2:b3'
                        },
                        input=INPUT,
                        output=OUTPUT,
                        label='split_corr_data:: Split corrected data from MS',
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailWSCLEAN(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('WSCLEAN_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
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
                                        "datacolumn"    :   "DATA2334",
                                        "prefix"        :   '%s:output' %(imname0),
                                },
                                input=INPUT,
                                output=OUTPUT,
                                label="image_target_field_r0:: Image target field first round",
                                time_out=300) 
                        recipe.run(resume=False)
                
        def testFailDDFacet(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('DDFACET_FAIL', ms_dir=MSDIR)
                imname=PREFIX+'ddfacet'
                with self.assertRaises(PipelineException):
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
                                        "Beam-FITSFile": "'baeseafdasms/JVLA-L-centred-$(xy)_$(reim).fits'",
                                        "Data-ChunkHours": 0.5,
                                        "Data-Sort": True,
                                        "Log-Boring": True,
                                        "Deconv-MaxMajorIter": 1,
                                        "Deconv-MaxMinorIter": 10,
                                },
                                input=INPUT, output=OUTPUT, shared_memory="36gb",
                                label="image_target_field_r0ddfacet:: Make a test image using ddfacet",
                                time_out=300) 
                        recipe.run(resume=False)
                
        def testFailPyBSDM(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('PYBDSM_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add("cab/pybdsm", "extract_init_model", {
                                "image"             :  '%s-MFS-image.fits:output' %(imname0),
                                "outfile"           :  '%s:output'%(lsm0),
                                "thresh_pix"        :  15,
                                "thresh_isl"        :  10,
                                "port2tigger"       :  True,
                                "multi_chan_beam"   :  True,
                                "beam_sp_derive"     :  True,
                                "spectralindex_do"   : True
                        },
                                input=INPUT, output=OUTPUT,
                                label="extract_init_model:: Make initial model from preselfcal image",
                                time_out=300) 
                        recipe.run(resume=False)
                
        def testFailPyMSUTILS(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('MSUTILS_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add("cab/msutils", "move_corrdata_to_data", {
                                "command"           : "copycol",
                                "msname"            : MS,
                                "fromcol"           : "CORRECTED324324_DA213TA",
                                "tocol"             : "DA23TA34",
                        },
                                input=INPUT, output=OUTPUT,
                                label="move_corrdata_to_data::msutils",
                                time_out=300) 
                        recipe.run(resume=False)
                        
        def testFailCalibrator(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('CALIBRATOR_FAIL', ms_dir=MSDIR)
                with self.assertRaises(PipelineException):
                        recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm0", {
                        "skymodel"           : "%s.ls5m.html:output"%(lsm0),
                        "msname"             : MS,
                        "threads"            : 16,
                        "column"             : "D1A2T3A4",
                        "output-data"        : "CORR_DATA",
                        "Gjones"             : True,
                        "Gjones-solution-intervals" : [20,64],     #Ad-hoc right now, subject to change
                        "Gjones-matrix-type" : "GainDiagPhase",
                        "write-flags-to-ms"  :  True,
                        "write-flagset"      : "ste2f3cal",
                        "read-legacy-flags"  : True,
                        "read-flags-from-ms" : True,
                        "read-flagsets"       : "-st1efc5al",    # ignore any stefcal flags that may exist
                        "Gjones-ampl-clipping"  :   True,
                        "Gjones-ampl-clipping-low"  :   0.15,
                        "Gjones-ampl-clipping-high" :   2.0,
                        "Gjones-thresh-sigma" :  10,
                        "Gjones-chisq-clipping" : False,
                        "make-plots"         : True,
                        "tile-size"          : 512,
                        },
                        input=INPUT, output=OUTPUT,
                        label="calibrator_Gjones_subtract_lsm0:: Calibrate and subtract LSM0",
                        time_out=300) 
                        recipe.run(resume=False)
                
        def testFailLWImager(self):
                global INPUT, OUTPUT, MSDIR, MS, LABEL, _nchans
                global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
                global REFANT, BPCAL, TARGET, GCAL, PREFIX
                global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
                global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1
                recipe = stimela.Recipe('LWIMAGER_FAIL', ms_dir=MSDIR)
                imname4 = PREFIX+"image4"
                with self.assertRaises(PipelineException):
                        recipe.add('cab/lwimager', 'lwimager_residue_cube', {
                                        "msname"            : MS,
                                        "column"            : "C1O2R3R4E5C6T7E8D9_1D12A3T4A5",
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
                                        "stokes"            : "IKASDW",
                                        "mode"              : "velocity"
                                },
                                input=OUTPUT,
                                output=OUTPUT,
                                label='lwimager_residue_cube:: make a cube after most of the continuum has'
                                        ' been cleaned and subtracted away',
                                time_out=300) 
                        recipe.run(resume=False)