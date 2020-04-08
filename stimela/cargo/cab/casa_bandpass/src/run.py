import os
import sys
import logging
import Crasa.Crasa as crasa
from casacore.tables import table
import numpy

sys.path.append("/scratch/stimela")

utils = __import__('utils')

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value

task = crasa.CasaTask(cab["binary"], **args)
task.run()


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

if not set(ids).issubset(field_ids):
    raise Runtime("Some field(s) do have solutions after the calibration. Please refer to CASA {task} logfile for further details".format(cab["prefix"]))
