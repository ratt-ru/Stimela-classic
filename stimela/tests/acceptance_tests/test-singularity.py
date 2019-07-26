import stimela
import os
import sys
import unittest
import subprocess
from nose.tools import timed
import shutil

class singularity_test(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
                unittest.TestCase.setUpClass()
                global INPUT, MSDIR, OUTPUT, MS, PREFIX, LSM
                INPUT=os.path.join(os.path.dirname(__file__), "input")
                MSDIR="msdir"
                global OUTPUT
                OUTPUT="/tmp/output_singularity"
                # MS name
                MS = "meerkat_simulation_example.ms"

                # Use the NVSS skymodel. This is natively available
                LSM = "nvss1deg.lsm.html"
                PREFIX = "stimela-example"  # Prefix for output images
                stimela.register_globals()
                if not "SINGULARITY_PULLFOLDER" in os.environ:
                    raise ValueError("ENV SINGULARITY_PULLFOLDER not set! This test requires singularity images to be pulled")

        @classmethod
        def tearDownClass(cls):
                unittest.TestCase.tearDownClass()
                global OUTPUT
                shutil.rmtree(OUTPUT)

        def tearDown(self):
                unittest.TestCase.tearDown(self)

        def setUp(self):
                unittest.TestCase.setUp(self)
         
        def testBasicSim(self):
            global INPUT, MSDIR, OUTPUT, MS, PREFIX, LSM

            # Start stimela Recipe instance
            pipeline = stimela.Recipe("Singularity Test",     # Recipe name
                              ms_dir=MSDIR,
                              singularity_image_dir=os.environ["SINGULARITY_PULLFOLDER"],
                              )

            pipeline.add("cab/simms",                   # Executor image to start container from 
                         "simms_example",               # Container name
                         { # Parameters to parse to executor container
                            "msname"    :   MS,                     
                            "telescope" :   "kat-7",              # Telescope name
                            "direction" :   "J2000,0deg,-30deg",    # Phase tracking centre of observation
                            "synthesis" :   0.128,                  # Synthesis time of observation
                            "dtime"     :   10,                      # Integration time in seconds
                            "freq0"     :   "750MHz",               # Start frequency of observation
                            "dfreq"     :   "1MHz",                 # Channel width
                            "nchan"     :   1                       # Number of channels
                         },
                         input=INPUT,                               # Input folder
                         output=OUTPUT,                             # Output folder
                         label="Creating MS",                       # Process label
                         cpus=2.5,
                         memory_limit="2gb",
                         time_out=300) 

            pipeline.add("cab/casa_listobs",
                         "listobs_example",
                         {
                             "vis"      : MS
                         },
                         input=INPUT,
                         output=OUTPUT,
                         label="Some obs details",
                         time_out=100) 

            pipeline.add("cab/simulator", 
                         "simulator_example",
                         {
                            "msname"    :   MS,
                            "skymodel"  :   LSM,                    # Sky model to simulate into MS
                            "addnoise"  :   True,                   # Add thermal noise to visibilities
                            "column"    :   "CORRECTED_DATA",       # Simulated data will be saved in this column
                            "sefd"      :   831,                    # Compute noise from this SEFD
                            "recenter"  :   True,                    # Recentre sky model to phase tracking centre of MS
                            "tile-size" : 64,
                            "threads"   : 4,
                         },
                        input=INPUT, output=OUTPUT,
                        label="Simulating visibilities",
                        time_out=600) 


#           pipeline.add('cab/casa_plotms', 
#                       'plot_vis',
#                       {
#                           "vis"           :   MS,
#                           "xaxis"         :   'uvdist',
#                           "yaxis"         :   'amp',
#                           "xdatacolumn"   :   'corrected',
#                           "ydatacolumn"   :   'corrected',
#                           "plotfile"      :   PREFIX+'-amp_uvdist.png',
#                           "overwrite"     :   True,
#                       },
#                       input=INPUT,
#                       output=OUTPUT,
#                       label='plot_amp_uvdist:: Plot amplitude vs uv-distance',
#                       time_out=600) 

            ## Image
            # Make things a bit interesting by imaging with different weights 
            # Briggs robust values to use for each image
            briggs_robust = [2]

            for i, robust in enumerate(briggs_robust):

                pipeline.add("cab/wsclean",
                             "imager_example_robust_{:d}".format(i), 
                             {
                                "msname"            :   MS,
                                "weight"            :   "briggs {:d}".format(i),
                                "prefix"            :   "{:s}_robust-{:d}".format(PREFIX, robust),
                                "npix"              :   2048,                   # Image size in pixels
                                "cellsize"          :   2,                      # Size of each square pixel
                                "clean_iterations"  :   1000,                   # Perform 1000 iterarions of clean (Deconvolution)
                             },
                             input=INPUT, 
                             output=OUTPUT, 
                             label="Imaging MS, robust={:d}".format(robust), 
                             cpus=2,
                             memory_limit="2gb",
                             time_out=600) 

            pipeline.add("cab/casa_rmtables", "delete_ms", {
                    "tablenames"    : MS + ":msfile",
                    },
                    input=INPUT,
                    output=OUTPUT,
                    label="Remove MS",
                    time_out=300) 



            # Run recipe. The 'steps' added above will be executed in the sequence that they were adde. The 'steps' added above will be
            # executed in the sequence that they were added
            pipeline.run()
