# -*- coding: future_fstrings -*-
import stimela
import os
import sys
import unittest
import subprocess
from nose.tools import timed
import shutil
import glob
from stimela.exceptions import *
from stimela.dismissable import dismissable as sdm
from stimela.pathformatter import pathformatter as spf
from stimela import cargo, singularity

class basicrecipe_test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()
        global INPUT, MSDIR, OUTPUT, MS, PREFIX, LSM, MS_SIM
        INPUT = os.path.join(os.path.dirname(__file__), "input")
        MSDIR = "msdir"
        global OUTPUT
        OUTPUT = "/tmp/output"

        # Start stimela Recipe instance
        import stimela.main as main
        os.chdir(os.path.dirname(__file__))
        cab = cargo.cab.CabDefinition(parameter_file="cab/custom/parameters.json")
        global SINGULARITY, PODMAN, UDOCKER
        SINGULARITY = False
        PODMAN = False
        UDOCKER = False
        if singularity.version and singularity.version >= "2.6.0":
            main.pull(["-s", "--force", "-im", f"stimela/base:{cab.tag}"])
            SINGULARITY = True
        #main.pull(["--force", "-im", f"stimela/base:{cab.tag}"])
        #main.pull(["-p", "--force", "-im", "stimela/base:1.2.0"])

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        global MSDIR
        global OUTPUT
        if os.path.exists(MSDIR):
            shutil.rmtree(MSDIR)
        if os.path.exists(OUTPUT):
            shutil.rmtree(OUTPUT)
        if os.path.exists(INPUT):
            shutil.rmtree(INPUT)
        if os.path.exists("stimela_parameter_files"):
            shutil.rmtree("stimela_parameter_files")
        for log in glob.glob("log-*"):
            os.remove(log)

    def setUp(self):
        unittest.TestCase.setUp(self)
        if not os.path.isdir(INPUT):
            os.mkdir(INPUT)

    def test_singularity(self):
        global MSDIR
        global INPUT
        global OUTPUT
        global SINGULARITY
        if SINGULARITY is False:
            return

        stimela.register_globals()
        rrr = stimela.Recipe("singularitypaths",
                             ms_dir=MSDIR,
                             JOB_TYPE="singularity",
                             cabpath="cab/",
                             singularity_image_dir=os.environ["SINGULARITY_PULLFOLDER"],
                             log_dir="logs")
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla5": ["testinput2.txt:input",
                     "testinput3.txt:msfile",
                     spf("{}hello\{reim\}.fits,{}to.fits,{}world.fits", "input", "msfile", "output")],
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run

        assert rrr.jobs[0].job._cab.parameters[4].value[0] == os.path.join(rrr.jobs[0].job.IODEST["input"], 
                    "testinput2.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[1] == os.path.join(rrr.jobs[0].job.IODEST["msfile"],
                    "testinput3.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[2] == \
                "{}/hello{{reim}}.fits,{}/to.fits,{}/world.fits".format(
                    rrr.jobs[0].job.IODEST["input"],
                    rrr.jobs[0].job.IODEST["msfile"],
                    rrr.jobs[0].job.IODEST["output"]
                )

    def test_udocker(self):
        import sys
        global MSDIR
        global INPUT
        global OUTPUT
        global UDOCKER
        if UDOCKER is False:
            return

        stimela.register_globals()
        rrr = stimela.Recipe("singularitypaths",
                             ms_dir=MSDIR,
                             JOB_TYPE="udocker",
                             cabpath="cab/",
                             log_dir="logs")
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla5": ["testinput2.txt:input",
                     "testinput3.txt:msfile",
                     spf("{}hello\{reim\}.fits,{}to.fits,{}world.fits", "input", "msfile", "output")],
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[4].value[0] == os.path.join(rrr.jobs[0].job.IODEST["input"], 
                    "testinput2.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[1] == os.path.join(rrr.jobs[0].job.IODEST["msfile"],
                    "testinput3.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[2] == \
                "{}/hello{{reim}}.fits,{}/to.fits,{}/world.fits".format(
                    rrr.jobs[0].job.IODEST["input"],
                    rrr.jobs[0].job.IODEST["msfile"],
                    rrr.jobs[0].job.IODEST["output"]
                )
    
    def test_podman(self):
        global MSDIR
        global INPUT
        global OUTPUT
        global PODMAN
        if PODMAN is False:
            return
        stimela.register_globals()
        rrr = stimela.Recipe("podmanpaths",
                             ms_dir=MSDIR,
                             JOB_TYPE="podman",
                             cabpath="cab/",
                             log_dir="logs")
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla5": ["testinput2.txt:input",
                     "testinput3.txt:msfile",
                     spf("{}hello\{reim\}.fits,{}to.fits,{}world.fits", "input", "msfile", "output")],
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[4].value[0] == os.path.join(rrr.jobs[0].job.IODEST["input"], 
                    "testinput2.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[1] == os.path.join(rrr.jobs[0].job.IODEST["msfile"],
                    "testinput3.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[2] == \
                "{}/hello{{reim}}.fits,{}/to.fits,{}/world.fits".format(
                    rrr.jobs[0].job.IODEST["input"],
                    rrr.jobs[0].job.IODEST["msfile"],
                    rrr.jobs[0].job.IODEST["output"]
                )

if __name__ == "__main__":
    unittest.main()
