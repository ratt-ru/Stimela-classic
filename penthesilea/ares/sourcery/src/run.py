import os
import sys
import json
import pyfits
import codecs
import subprocess

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
OUTDIR = os.environ["OUTPUT"]
MAC_OS = os.environ["MAC_OS"]

if MAC_OS.lower() in ["yes", "true", "yebo", "1"]:
    MAC_OS = True
else:
    MAC_OS = False


jdict = utils.readJson(CONFIG)
template = utils.readJson("sourcery_template.json")

name = INDIR+"/"+jdict["imagename"]
psf = INDIR+"/"+jdict["psf"]

template["imagename"] = name
template["psfname"] = psf
template["reliability"]["thresh_pix"] = jdict["thresh"]

output = "./temp-directory-xaba"
template["outdir"] = output if MAC_OS else OUTDIR

config = "run_me_now.json"
utils.writeJson(config, template)

utils.xrun("sourcery", ["-jc", config])

utils.xrun("rm", ["-f", config])

if MAC_OS:
    utils.xrun("mv", [output, OUTDIR])


