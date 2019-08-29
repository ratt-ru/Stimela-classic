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
        global INPUT, MSDIR, OUTPUT, MS, PREFIX, LSM, MS_SIM
        INPUT = os.path.join(os.path.dirname(__file__), "input")
        MSDIR = "msdir"
        global OUTPUT
        OUTPUT = "/tmp/output_singularity"
        # MS name
        MS_SIM = "meerkat_simulation_example.ms"
        MS = "kat-7-small.ms"

        # Use the NVSS skymodel. This is natively available
        LSM = "nvss1deg.lsm.html"
        PREFIX = "stimela-example"  # Prefix for output images
        stimela.register_globals()
        if not "SINGULARITY_PULLFOLDER" in os.environ:
            raise ValueError(
                "ENV SINGULARITY_PULLFOLDER not set! This test requires singularity images to be pulled")

    @classmethod
    def tearDownClass(cls):
        unittest.TestCase.tearDownClass()
        global OUTPUT
        shutil.rmtree(OUTPUT)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testSingularity(self):
        global INPUT, MSDIR, OUTPUT, MS, MS_SIM

        # Start stimela Recipe instance
        pipeline = stimela.Recipe("Singularity Test",     # Recipe name
                                  ms_dir=MSDIR,
                                  singularity_image_dir=os.environ["SINGULARITY_PULLFOLDER"],
                                  )

        pipeline.add("cab/simms",                   # Executor image to start container from
                     "simms_example",               # Container name
                     {  # Parameters to parse to executor container
                        "msname":   MS_SIM,
                        "telescope":   "kat-7",              # Telescope name
                        "direction":   "J2000,0deg,-30deg",    # Phase tracking centre of observation
                        "synthesis":   0.128,                  # Synthesis time of observation
                        "dtime":   10,                      # Integration time in seconds
                        "freq0":   "750MHz",               # Start frequency of observation
                        "dfreq":   "1MHz",                 # Channel width
                        "nchan":   1                       # Number of channels
                     },
                     input=INPUT,                               # Input folder
                     output=OUTPUT,                             # Output folder
                     label="Creating MS",                       # Process label
                     cpus=2.5,
                     memory_limit="2gb",
                     time_out=300)

        # Run recipe. The 'steps' added above will be executed in the sequence that they were adde. The 'steps' added above will be
        # executed in the sequence that they were added
        pipeline.run()

    def testUdocker(self):
        global INPUT, MSDIR, OUTPUT, MS

        if sys.version_info <= (3, 0):

            pipeline = stimela.Recipe("Udocker Test",
                                      ms_dir=MSDIR,
                                      JOB_TYPE="udocker",
                                      )

            pipeline.add("cab/tricolour",
                         "simms_example",
                         {
                             "ms": MS,
                             "flagging-strategy": "standard",
                         },
                         input=INPUT,
                         output=OUTPUT,
                         cpus=2.5,
                         memory_limit="2gb",
                         time_out=300)

            pipeline.run()


#       def testPodman(self):
#           global INPUT, MSDIR, OUTPUT, MS

#           pipeline = stimela.Recipe("Podman Test",
#                             ms_dir=MSDIR,
#                             JOB_TYPE="podman",
#                             )

#           pipeline.add("cab/casa_listobs",
#                        "simms_example",
#                        {
#                           "vis"       :   MS,
#                           "listfile"  :   "obsinfo.txt",
#                        },
#                        input=INPUT,
#                        output=OUTPUT,
#                        cpus=2.5,
#                        memory_limit="2gb",
#                        time_out=300)

#           pipeline.run()
