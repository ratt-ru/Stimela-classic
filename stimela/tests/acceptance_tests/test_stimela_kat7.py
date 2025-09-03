import stimela
import os
import unittest


class TestKat7Reduce(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()
        # I/O
        global INPUT
        INPUT = 'input'
        global MSDIR
        MSDIR = 'msdir'

        global MS
        MS = 'kat-7-small.ms'
        global PREFIX
        PREFIX = 'kat7_small_LBand'

        # Fields
        global GCAL
        GCAL = 'PKS2326-477'
        global TARGET
        TARGET = '1'
        global BPCAL
        BPCAL = 'PKS1934-638'

        # Reference antenna
        global REFANT
        REFANT = '0'

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

        global LABEL
        LABEL = "test_reduction"
        global OUTPUT
        OUTPUT = "output_%s" % LABEL
        global MSCONTSUB
        MSCONTSUB = MS + '.contsub'

        global SPW
        SPW = '0:100~355'
        # Calibration tables
        global LSM0
        LSM0 = PREFIX + '.lsm.html'
        global SELFCAL_TABLE1
        SELFCAL_TABLE1 = PREFIX + '.SF1:output'
        global IMAGE1
        IMAGE1 = PREFIX + 'image1:output'
        global MASK1
        MASK1 = PREFIX + 'mask1.fits'
        global IMAGE2
        IMAGE2 = PREFIX + 'image2:output'
        global nchans
        nchans = 256
        global chans
        chans = [100, 355]

        # Clean-Mask-Clean
        global imname0
        imname0 = PREFIX + 'image0'
        global maskname0
        maskname0 = PREFIX + 'mask0.fits'
        global maskname01
        maskname01 = PREFIX + 'mask01.fits'
        global imname1
        imname1 = PREFIX + 'image1'
        global corr_ms
        corr_ms = MS + '-corr.ms'
        global lsm0
        lsm0 = PREFIX + '-LSM0'
        stimela.register_globals()

    @classmethod
    def tearDownClass(cls):
        unittest.TestCase.tearDownClass()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_end_to_end_reduction(self):
        global INPUT, OUTPUT, MSDIR, MS, LABEL
        global GAINCAL_TABLE2, FLUXSCALE_TABLE, GAINCAL_TABLE, DELAYCAL_TABLE, BPCAL_TABLE, ANTPOS_TABLE
        global REFANT, BPCAL, TARGET, GCAL, PREFIX
        global MSCONTSUB, SPW, LSM0, SELFCAL_TABLE1, corr_ms, lsm0
        global IMAGE1, IMAGE2, MASK1, nchans, chans, imname0, maskname0, maskname01, imname1

        recipe = stimela.Recipe('Test reduction script',
                                ms_dir=MSDIR, JOB_TYPE="docker", log_dir="logs")

        recipe.add('cab/casa_listobs', 'listobs', {
            "vis": MS
        },
            input=INPUT,
            output=OUTPUT,
            label='listobs:: some stats',
            time_out=300)

        recipe.add("cab/owlcat_plotelev", "plotobs", {
            "msname" : MS,
            "output-name" : "obsplot.png",
        },
            input=INPUT,
            output=OUTPUT,
            label="plotobs:: Plot elevation/azimuth vs LST/UTC")

        # It is common for the array to require a small amount of time to settle down at the start of a scan. Consequently, it has
        # become standard practice to flag the initial samples from the start
        # of each scan. This is known as 'quack' flagging
        recipe.add('cab/casa_flagdata', 'quack_flagging', {
            "vis": MS,
            "mode": 'quack',
            "quackinterval": 10.0,
            "quackmode": 'beg',
        },
            input=INPUT,
            output=OUTPUT,
            label='quack_flagging:: Quack flagging',
            time_out=300)

        # Flag the autocorrelations
        recipe.add("cab/politsiyakat_autocorr_amp", "flag_autopower", {
            "msname": MS,
            "field": "0,1,2",
            "cal_field": "0,2",
            "nrows_chunk": 5000,
            "scan_to_scan_threshold": 1.5,
            "antenna_to_group_threshold": 4,
            "nio_threads": 1,
            "nproc_threads": 32,
            },input=INPUT, output=OUTPUT, label="flag_autopower")

        recipe.add('cab/casa_flagdata', 'autocorr_flagging', {
            "vis":   MS,
            "mode":   'manual',
            "autocorr":   True,
        },
            input=INPUT,
            output=OUTPUT,
            label='autocorr_flagging:: Autocorrelations flagging',
            time_out=300)

        # Flag bad channels
        recipe.add('cab/casa_flagdata', 'badchan_flagging', {
            "vis":   MS,
            "mode":   'manual',
            "spw":   "0:113~113,0:313~313,0:369~369,0:601~607,0:204~204,0:212~212,0:594~600",

        },
            input=INPUT,
            output=OUTPUT,
            label='badchan_flagging:: Bad Channel flagging',
            time_out=300)

        recipe.add('cab/casa_clearcal', 'clearcal',
                   {
                       "vis":   MS,
                       "addmodel":   True
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='clearcal:: casa clearcal',
                   time_out=300)

        recipe.add('cab/casa_setjy', 'set_flux_scaling', {
            "vis":   MS,
            "field":   BPCAL,
            "standard":   'Perley-Butler 2010',
            "usescratch":   True,
            "scalebychan":   True,
        },
            input=INPUT,
            output=OUTPUT,
            label='set_flux_scaling:: Set flux density value for the amplitude calibrator',
            time_out=300)

        recipe.add('cab/casa_bandpass', 'bandpass_cal', {
            "vis": MS,
            "caltable": BPCAL_TABLE,
            "field": BPCAL,
            "refant": REFANT,
            "spw": SPW,
            "solint": 'inf',
            "bandtype": 'B',
            #                        "opacity"   : 0.0,
            #                        "gaincurve" : False,
        },
            input=INPUT,
            output=OUTPUT,
            label='bandpass_cal:: Bandpass calibration',
            time_out=300)

        recipe.add('cab/ragavi', 'ragavi_gains_plot_bandpass', {
                   'table': BPCAL_TABLE,
                   'gaintype': "B",
                   'htmlname': PREFIX + '_B0_amp_chan'
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='ragavi_gains_plot_bandpass:: Plot bandpass table',
                   time_out=1200
                   )

        # display the bandpass solutions. Note that in the plotcal inputs below, the amplitudes are being displayed as a function of
        # frequency channel. The parameter subplot=221 is used to display multiple plots per page (2 plots per page in the y
        # direction and 2 in the x direction). The first two commands below show the amplitude solutions (one per each polarization)
        # and the last two show the phase solutions (one per each polarization). Parameter iteration='antenna' is used to step
        # through separate plots for each antenna.
        recipe.add('cab/casa_plotcal', 'plot_bandpass_amp_R', {
            "caltable": BPCAL_TABLE,
            "poln": 'R',
            "xaxis": 'chan',
            "yaxis": 'amp',
            "field": BPCAL,
            "spw": SPW,
            "subplot": 221,
            "figfile": PREFIX + '-B0-R-amp.png',
        },
            input=INPUT,
            output=OUTPUT,
            label='plot_bandpass_amp_R:: Plot bandpass table. AMP, R',
            time_out=1200)

        # Gain calibration - amplitude and phase - first for BPCAL.
        recipe.add('cab/casa_gaincal', 'gaincal_bp', {
            "vis": MS,
            "caltable": GAINCAL_TABLE,
            "field": "{0:s},{1:s}".format(BPCAL, GCAL),
            "solint": 'inf',
            "refant": '',
            "gaintype": 'G',
            "calmode": 'ap',
            "spw": SPW,
            "solnorm": False,
            "gaintable": [BPCAL_TABLE],
            "interp": ['nearest'],
        },
            input=INPUT,
            output=OUTPUT,
            label="gaincal:: Gain calibration",
            time_out=300, 
            version=None)

        # Set fluxscale
        recipe.add('cab/casa_fluxscale', 'fluxscale', {
            "vis": MS,
            "caltable": GAINCAL_TABLE,
            "fluxtable": FLUXSCALE_TABLE,
            "reference": [BPCAL],
            "transfer": [GCAL],
            "save_result" : "fluxinfo.pickle",
            "incremental": False,
        },
            input=INPUT,
            output=OUTPUT,
            label='fluxscale:: Set fluxscale',
            time_out=300)

        # Apply calibration to BPCAL
        recipe.add('cab/casa_applycal', 'applycal_bp', {
            "vis": MS,
            "field": BPCAL,
            "gaintable": [BPCAL_TABLE, FLUXSCALE_TABLE],
            "gainfield": ['', '', BPCAL],
            "interp": ['', '', 'nearest'],
            "calwt": [False],
            "parang": False,
            "applymode": "calflag",
        },
            input=INPUT,
            output=OUTPUT,
            label='applycal_bp:: Apply calibration to Bandpass Calibrator',
            time_out=1800)

        # Flag the phase
        recipe.add("cab/politsiyakat_cal_phase", "flag_calphase", {
            "msname": MS,
            "field": ",".join(["0","1","2"]),
            "cal_field": ",".join(["0","2"]),
            "nrows_chunk": 5000,
            "data_column": "CORRECTED_DATA",
            "scan_to_scan_threshold": 1.5,
            "baseline_to_group_threshold": 4,
            "nio_threads": 1,
            "nproc_threads": 32,
            },input=INPUT, output=OUTPUT, label="flag_calphase")

        recipe.run()

        recipe = stimela.Recipe('KAT reduction script 2',
                                ms_dir=MSDIR, JOB_TYPE="docker", log_dir="logs")
        # Copy CORRECTED_DATA to DATA, so we can start uv_contsub
        recipe.add("cab/msutils", "move_corrdata_to_data", {
            "command": "copycol",
            "msname": MS,
            "fromcol": "CORRECTED_DATA",
            "tocol": "DATA",
        },
            input=INPUT, output=OUTPUT,
            label="move_corrdata_to_data::msutils",
            time_out=1800)

        os.system("rm -rf {}/{}-corr.ms".format(MSDIR, MS[:-3]))
        recipe.add('cab/casa_split', 'split_corr_data',
                   {
                       "vis":   MS,
                       "outputvis":   MS[:-3] + '-corr.ms',
                       "field":   str(BPCAL),
                       "spw":   SPW,
                       "datacolumn":   'data',
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='split_corr_data:: Split corrected data from MS',
                   time_out=1800)

        MS = MS[:-3] + '-corr.ms'

        recipe.add('cab/casa_clearcal', 'prep_split_data',
                   {
                       "vis":   MS,
                       "addmodel":   True
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='prep_split_data:: Prep split data with casa clearcal',
                   time_out=1800)

        # Clean-Mask-Clean
        imname0 = PREFIX + 'image0'
        maskname0 = PREFIX + 'mask0.fits'
        maskname01 = PREFIX + 'mask01.fits'
        imname1 = PREFIX + 'image1'

        recipe.add('cab/casa_tclean', 'image_target_field_r1', {
            "vis":   MS,
            "datacolumn":  "corrected",
            "field":   "0",
            "start":   21,  # Other channels don't have any data
            "nchan":   235 - 21,
            "width":   1,
            # Use Briggs weighting to weigh visibilities for imaging
            "weighting":   "briggs",
            "robust":   0,
            "imsize":   256,                   # Image size in pixels
            "cellsize":   "30arcsec",                      # Size of each square pixel
            "niter":   100,
            "stokes":   "I",
            "prefix":   '%s:output' % (imname1),
        },
            input=INPUT,
            output=OUTPUT,
            label="image_target_field_r1:: Image target field second round",
            time_out=300)

        recipe.add('cab/cleanmask', 'mask0', {
            "image": '%s.image.fits:output' % (imname1),
            "output": '%s:output' % (maskname0),
            "dilate": False,
            "sigma": 20,
        },
            input=INPUT,
            output=OUTPUT,
            label='mask0:: Make mask',
            time_out=1800)

        lsm0 = PREFIX + '-LSM0'
        # Source finding for initial model
        recipe.add("cab/pybdsm", "extract_init_model", {
            "image":  '%s.image.fits:output' % (imname1),
            "outfile":  '%s:output' % (lsm0),
            "thresh_pix":  25,
            "thresh_isl":  15,
            "port2tigger":  True,
        },
            input=INPUT, output=OUTPUT,
            label="extract_init_model:: Make initial model from preselfcal image",
            time_out=1800)

        # First selfcal round

        recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm0", {
            "skymodel": "%s.lsm.html:output" % (lsm0),
            "msname": MS,
            "threads": 16,
            "column": "DATA",
            "output-data": "CORR_RES",
            "Gjones": True,
            # Ad-hoc right now, subject to change
            "Gjones-solution-intervals": [20, 0],
            "Gjones-matrix-type": "GainDiagPhase",
            "tile-size": 512,
            "field-id": 0,
        },
            input=INPUT, output=OUTPUT,
            label="calibrator_Gjones_subtract_lsm0:: Calibrate and subtract LSM0",
            time_out=1800)

        # Diversity is a good thing... lets add some DDFacet to this soup bowl
        imname = PREFIX + 'ddfacet'

        recipe.add("cab/ddfacet", "ddfacet_test",
                   {
                       "Data-MS": [MS],
                       "Output-Name": imname,
                       "Image-NPix": 256,
                       "Image-Cell": 30,
                       "Cache-Reset": True,
                       "Freq-NBand": 2,
                       "Weight-ColName": "WEIGHT",
                       "Data-ChunkHours": 10,
                       "Beam-FITSFeed": "rl",
                       "Data-Sort": True,
                       "Log-Boring": True,
                       "Deconv-MaxMajorIter": 1,
                       "Deconv-MaxMinorIter": 20,
                   },
                   input=INPUT, output=OUTPUT, shared_memory="8gb",
                   label="image_target_field_r0ddfacet:: Make a test image using ddfacet",
                   time_out=520)

        lsm1 = PREFIX + '-LSM0'
        # Source finding for initial model
        recipe.add("cab/pybdsm", "extract_init_model", {
            "image":  '%s.app.restored.fits:output' % (imname),
            "outfile":  '%s:output' % (lsm1),
            "thresh_pix":  25,
            "thresh_isl":  15,
            "port2tigger":  True,
        },
            input=INPUT, output=OUTPUT,
            label="extract_init_model:: Make initial model from preselfcal image",
            time_out=1800)

        # Stitch LSMs together
        lsm2 = PREFIX + '-LSM2'
        recipe.add("cab/tigger_convert", "stitch_lsms1", {
            "input-skymodel":   "%s.lsm.html:output" % lsm0,
            "output-skymodel":   "%s.lsm.html:output" % lsm2,
            "rename": True,
            "force": True,
            "append":   "%s.lsm.html:output" % lsm1,
        },
            input=INPUT, output=OUTPUT,
            label="stitch_lsms1::Create master lsm file",
            time_out=300)

        recipe.add("cab/calibrator", "calibrator_Gjones_subtract_lsm0", {
            "skymodel": "%s.lsm.html:output" % (lsm2),
            "msname": MS,
            "threads": 16,
            "column": "DATA",
            "output-data": "CORR_RES",
            "Gjones": True,
            # Ad-hoc right now, subject to change
            "Gjones-solution-intervals": [20, 0],
            "Gjones-matrix-type": "GainDiagPhase",
            "tile-size": 512,
            "field-id": 0,
        },
            input=INPUT, output=OUTPUT,
            label="calibrator_Gjones_subtract_lsm0:: Calibrate and subtract LSM0",
            time_out=1800)

        recipe.add('cab/casa_uvcontsub', 'uvcontsub',
                   {
                       "msname":    MS,
                       "field":    "0",
                       "fitorder":    1,
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='uvcontsub:: Subtract continuum in the UV plane',
                   time_out=1800)

        # Image HI
        recipe.add('cab/casa_clean', 'casa_dirty_cube',
                   {
                       "msname": MS + ".contsub",
                       "prefix": PREFIX,
                       "mode": 'channel',
                       "nchan": nchans,
                       "niter": 0,
                       "npix": 256,
                       "cellsize": 30,
                       "weight": 'natural',
                       "port2fits": True,
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='casa_dirty_cube:: Make a dirty cube with CASA CLEAN',
                   time_out=1800)

        recipe.add('cab/sofia', 'sofia',
                   {
                       #    USE THIS FOR THE WSCLEAN DIRTY CUBE
                       #    "import.inFile"     :   '{:s}-cube.dirty.fits:output'.format(combprefix),
                       #    USE THIS FOR THE CASA CLEAN CUBE
                       # CASA CLEAN cube
                       "import.inFile":   '{:s}.image.fits:output'.format(PREFIX),
                       "steps.doFlag": False,
                       "steps.doScaleNoise": True,
                       "steps.doSCfind": True,
                       "steps.doMerge": True,
                       "steps.doReliability": False,
                       "steps.doParameterise": False,
                       "steps.doWriteMask": True,
                       "steps.doMom0": False,
                       "steps.doMom1": False,
                       "steps.doWriteCat": True,
                       "flag.regions": [],
                       "scaleNoise.statistic": 'mad',
                       "SCfind.threshold": 4,
                       "SCfind.rmsMode": 'mad',
                       "merge.radiusX": 2,
                       "merge.radiusY": 2,
                       "merge.radiusZ": 2,
                       "merge.minSizeX": 2,
                       "merge.minSizeY": 2,
                       "port2tigger": False,
                       "merge.minSizeZ": 2,
                   },
                   input=INPUT,
                   output=OUTPUT,
                   label='sofia:: Make SoFiA mask and images',
                   time_out=1800)

        recipe.run()
