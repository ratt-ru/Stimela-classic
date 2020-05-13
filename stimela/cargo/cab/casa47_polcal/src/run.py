import os
import sys
import logging
import Crasa.Crasa as crasa
from casacore.tables import table
import numpy
import glob
import yaml
import shutil

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

with open(CONFIG, "r") as _std:
    cab = yaml.safe_load(_std)

junk = cab["junk"]

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value

task = crasa.CasaTask(cab["binary"], **args)
try:
    task.run()
finally:
    for item in junk:
        for dest in [OUTPUT, MSDIR]: # these are the only writable volumes in the container
            items = glob.glob("{dest}/{item}".format(**locals()))
            for f in items:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
                # Leave other types

gtab = args["caltable"]
if not os.path.exists(gtab):
    raise RuntimeError("The gaintable was not created. Please refer to CASA {0:s} logfile for further details".format(cab["binary"]))

tab = table(gtab)
field_ids = numpy.unique(tab.getcol("FIELD_ID"))
tab.close()

tab = table(gtab+"::FIELD")
field_names = tab.getcol("NAME")
tab.close()

field_in = args["field"].split(",")

try:
    ids = map(int, field_in)
except ValueError:
    ids = map(lambda a: field_names.index(a), field_in)

if not set(ids).intersection(field_ids):
    raise RuntimeError("None of the fields has solutions after the calibration. Please refer to CASA the {} logfile for further details".format(cab["binary"]))
