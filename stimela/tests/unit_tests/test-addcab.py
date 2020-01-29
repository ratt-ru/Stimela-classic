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
        main.build(["-c", "custom,cab/custom"])
        main.pull(["-s", "--force", "-im", "stimela/base:1.2.0"])
        if sys.version_info[0] == 2:
            main.pull(["--force", "-im", "stimela/base:1.2.0"])

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

    def test_define_cab(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("customcab", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a"
        }, input=INPUT, output=OUTPUT)
        assert len(rrr.jobs) == 1
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[0].value == "a"
        assert len(rrr.completed) == 1
        assert len(rrr.remaining) == 0

    def test_invalid_choice(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("invchoice", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
        "bla1": "d" # only accepts a, b or c
        }, input=INPUT, output=OUTPUT)
        with self.assertRaises(PipelineException):
            rrr.run() #validate and run

    def test_dismissable(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("testdismissable", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla4": sdm("abc"),
            "bla3": sdm(None)
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[0].value == "a"
        assert rrr.jobs[0].job._cab.parameters[1].value is None
        assert rrr.jobs[0].job._cab.parameters[2].value is None
        assert rrr.jobs[0].job._cab.parameters[3].value == ["abc"]

    def test_floattypefail(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("testfloattypefail", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla3": "1.0a",
        }, input=INPUT, output=OUTPUT)
        with self.assertRaises(PipelineException):
            rrr.run() #validate and run

    def test_floattypesuccess(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("testfloattypesuccess", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla3": 4.0,
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[2].value == [4.0]

    def test_required(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("testrequired", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla3": 4.0,
        }, input=INPUT, output=OUTPUT)
        with self.assertRaises(PipelineException):
            rrr.run() #validate and run

    def test_iooverride(self):
        global MSDIR
        global INPUT
        with open(os.path.join(INPUT, "testinput.txt"), "w+") as f:
            pass
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("testiooverrides", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla2": "testinput.txt:input",
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[0].value == "a"
        assert rrr.jobs[0].job._cab.parameters[1].value == "/input/testinput.txt"

    def test_iopathval(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("ioval", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla2": "testinput2.txt:input",
        }, input=INPUT, output=OUTPUT)
        with self.assertRaises(PipelineException): # not exist during validation
            rrr.run() #validate and run

    def test_iopathlist(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("pathlist", ms_dir=MSDIR)
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla5": ["testinput2.txt:input",
                     "testinput3.txt:msfile",
                     spf("{}hello\{reim\}.fits,{}to.fits,{}world.fits", "input", "msfile", "output")],
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[4].value[0] == "/input/testinput2.txt"
        assert rrr.jobs[0].job._cab.parameters[4].value[1] == os.path.join("/",
                                                                           "home",
                                                                           os.environ["USER"],
                                                                           "msdir",
                                                                           "testinput3.txt")
        assert rrr.jobs[0].job._cab.parameters[4].value[2] == \
                "{}hello{{reim}}.fits,{}to.fits,{}world.fits".format(
                    "/input/",
                    os.path.join("/", "home", os.environ["USER"], "msdir/"),
                    os.path.join("/", "home", os.environ["USER"], "output/"),
                )

    def test_singularity(self):
        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("singularitypaths",
                             ms_dir=MSDIR,
                             JOB_TYPE="singularity",
                             cabpath="cab/",
                             singularity_image_dir=os.environ["SINGULARITY_PULLFOLDER"])
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla5": ["testinput2.txt:input",
                     "testinput3.txt:msfile",
                     spf("{}hello\{reim\}.fits,{}to.fits,{}world.fits", "input", "msfile", "output")],
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run

        assert rrr.jobs[0].job._cab.parameters[4].value[0] == "/scratch/input/testinput2.txt"
        assert rrr.jobs[0].job._cab.parameters[4].value[1] == "/scratch/msdir/testinput3.txt"
        assert rrr.jobs[0].job._cab.parameters[4].value[2] == \
                "{}hello{{reim}}.fits,{}to.fits,{}world.fits".format(
                    "/scratch/input/",
                    "/scratch/msdir/",
                    "/scratch/output/"
                )


    def test_udocker(self):
        import sys
        if sys.version_info[0] > 2:
            return

        global MSDIR
        global INPUT
        global OUTPUT
        stimela.register_globals()
        rrr = stimela.Recipe("singularitypaths",
                             ms_dir=MSDIR,
                             JOB_TYPE="udocker",
                             cabpath="cab/")
        assert os.path.exists(MSDIR)
        rrr.add("cab/custom", "test1", {
            "bla1": "a", # only accepts a, b or c
            "bla5": ["testinput2.txt:input",
                     "testinput3.txt:msfile",
                     spf("{}hello\{reim\}.fits,{}to.fits,{}world.fits", "input", "msfile", "output")],
        }, input=INPUT, output=OUTPUT)
        rrr.run() #validate and run
        assert rrr.jobs[0].job._cab.parameters[4].value[0] == "/scratch/input/testinput2.txt"
        assert rrr.jobs[0].job._cab.parameters[4].value[1] == "/scratch/msdir/testinput3.txt"
        assert rrr.jobs[0].job._cab.parameters[4].value[2] == \
                "{}hello{{reim}}.fits,{}to.fits,{}world.fits".format(
                    "/scratch/input/",
                    "/scratch/msdir/",
                    "/scratch/output/"
                )

if __name__ == "__main__":
    unittest.main()
