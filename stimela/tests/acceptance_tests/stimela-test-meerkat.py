# -*- coding: future_fstrings -*-
import stimela
import os
import unittest
import subprocess
from nose.tools import timed
import shutil


class mk_reduce(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()
        # I/O
        global INPUT
        INPUT = 'input'
        global MSDIR
        MSDIR = 'msdir'

        global MS
        MS = '1491291289.1GC.ms'
        global PREFIX
        PREFIX = 'deep2'

        global LABEL
        LABEL = "test_mkreduction"
        global OUTPUT
        OUTPUT = "output_%s" % LABEL

        stimela.register_globals()

    @classmethod
    def tearDownClass(cls):
        unittest.TestCase.tearDownClass()
        #global OUTPUT
        #shutil.rmtree(OUTPUT)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def setUp(self):
        unittest.TestCase.setUp(self)

    def testEndToEndReduction(self):
        global INPUT, OUTPUT, MSDIR, MS, LABEL
        recipe = stimela.Recipe('Test reduction script',
                                ms_dir=MSDIR, JOB_TYPE="docker", log_dir="logs")
        imname1 = "deep2.1gc"
        imname2 = "deep2.2gc"
        recipe.add("cab/ddfacet", "ddfacet_test1",
                   {
                       "Data-MS": [MS],
                       "Output-Name": imname1,
                       "Image-NPix": 5000,
                       "Image-Cell": 1.6,
                       "Cache-Reset": True,
                       "Freq-NBand": 2,
                       "Freq-NDegridBand": 6,
                       "Weight-ColName": "WEIGHT",
                       "Data-ChunkHours": 0.1,
                       "Data-Sort": True,
                       "Log-Boring": True,
                       "Deconv-MaxMajorIter": 3,
                       "Deconv-MaxMinorIter": 500,
                   },
                   input=INPUT, output=OUTPUT, shared_memory="8gb",
                   label="image1",
                   time_out=1800)

        maskname0 = "MASK.fits"
        recipe.add('cab/cleanmask', 'mask0', {
            "image": '%s.app.restored.fits:output' % (imname1),
            "output": '%s:output' % (maskname0),
            "dilate": False,
            "sigma": 25,
        },
            input=INPUT,
            output=OUTPUT,
            label='mask0:: Make mask',
            time_out=1800)

        recipe.add("cab/ddfacet", "ddfacet_test2",
                   {
                       "Data-MS": [MS],
                       "Output-Name": imname1,
                       "Image-NPix": 5000,
                       "Image-Cell": 1.6,
                       "Cache-Reset": True,
                       "Freq-NBand": 2,
                       "Freq-NDegridBand": 6,
                       "Mask-External": '%s:output' % (maskname0),
                       "Weight-ColName": "WEIGHT",
                       "Data-ChunkHours": 0.1,
                       "Data-Sort": True,
                       "Log-Boring": True,
                       "Deconv-MaxMajorIter": 3,
                       "Deconv-MaxMinorIter": 1500,
                   },
                   input=INPUT, output=OUTPUT, shared_memory="24gb",
                   label="image2",
                   time_out=1800)
        
        recipe.add('cab/tricolour', "flag_data",
        {
                  "ms"                  : MS,
                  "data-column"         : "DATA",
                  "window-backend"      : 'numpy',
                  "field-names"         : 0,
                  "flagging-strategy"   : "total_power",
                  "subtract-model-column": "MODEL_DATA",
        },
        input=INPUT, output=OUTPUT, label="flag_data")

        # First selfcal round

        recipe.add("cab/cubical", "cubical_cal", {
                'data-ms': MS,
                'data-column': "DATA",
                'dist-nworker': 4,
                'dist-nthread': 1,
                'dist-max-chunks': 20, 
                'data-freq-chunk': 0,
                'data-time-chunk': 5,
                'model-list': "MODEL_DATA",
                'weight-column': "WEIGHT",
                'flags-apply': "FLAG",
                'flags-auto-init': "legacy",
                'madmax-enable': False,
                'madmax-threshold': [0,0,10],
                'madmax-global-threshold': [0,0],
                'sol-jones': 'g',
                'sol-stall-quorum': 0.95,
                'out-name': "cubicaltest",
                'out-column': "CORRECTED_DATA",
                'log-verbose': "solver=2",
                'g-type': "complex-2x2",
                'g-freq-int': 0,
                'g-time-int': 20,
                'g-max-iter': 20,
                'g-update-type': "complex-2x2",
                 
            }, input=INPUT, output=OUTPUT, 
            label="cubical",
            shared_memory="24gb",
            time_out=1800)

        recipe.add("cab/ddfacet", "ddfacet_test3",
                   {
                       "Data-MS": [MS],
                       "Output-Name": imname2,
                       "Image-NPix": 5000,
                       "Image-Cell": 1.6,
                       "Data-ColName": "CORRECTED_DATA",
                       "Cache-Reset": True,
                       "Freq-NBand": 2,
                       "Freq-NDegridBand": 6,
                       "Mask-External": '%s:output' % (maskname0),
                       "Weight-ColName": "WEIGHT",
                       "Data-ChunkHours": 0.1,
                       "Data-Sort": True,
                       "Log-Boring": True,
                       "Deconv-MaxMajorIter": 3,
                       "Deconv-MaxMinorIter": 1500,
                   },
                   input=INPUT, output=OUTPUT, shared_memory="24gb",
                   label="image3",
                   time_out=1800)

        recipe.run()
