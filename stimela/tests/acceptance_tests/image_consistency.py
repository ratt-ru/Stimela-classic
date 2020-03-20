import stimela
import os
import unittest
import subprocess
from nose.tools import timed
import shutil
from stimela.cargo import cab
import os
import json


class kat7_reduce(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()
        global CAB_PATH
        CAB_PATH = os.path.abspath(os.path.dirname(cab.__file__))
  
    @classmethod
    def tearDownClass(cls):
        unittest.TestCase.tearDownClass()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_images(self):
        global CAB_PATH
        allfiles = os.listdir(CAB_PATH)
        nomatch = []
        for item in os.listdir(CAB_PATH):
            cabpath = os.path.join(CAB_PATH, item)
            parfile = os.path.join(CAB_PATH, item, "parameters.json")
            if os.path.isdir(cabpath) and os.path.exists(parfile):
                pass
            else:
                continue
            dockerfile = os.path.join(CAB_PATH, item, "Dockerfile")
            # First get base image from json file
            with open(parfile, "r") as stdr:
                cabdict = json.load(stdr)
                parfile_base = ":".join([cabdict["base"], cabdict["tag"]])

            with open(dockerfile, "r") as stdr:
                for line in stdr.readlines():
                    if line.strip().lower().startswith("from"):
                        line_ = line.split("#")[0]
                        dfile_base = line_.split()[-1].strip()
                        break
            if dfile_base != parfile_base:
                nomatch.append(item)
        if nomatch:
            raise RuntimeError("These cabs have inconsistent base images in"
                               " parameters.json and Dockerfile: {0:s}".format(",".join(nomatch)))
