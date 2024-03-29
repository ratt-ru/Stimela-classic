# -*- coding: future_fstrings -*-
import Crasa.Crasa as crasa
from scabha import config, parameters_dict, prun
from casacore.table import table
import os
import numpy

print(f"Running CASA task '{config.binary}'")

args = parameters_dict

task = crasa.CasaTask(config.binary, **args)
task.run()

gtab = args["caltable"]
if not os.path.exists(gtab):
    raise RuntimeError(f"The gaintable was not created. Please refer to CASA {config.binary} logfile for further details")

tab = table(gtab)
field_ids = numpy.unique(tab.getcol("FIELD_ID"))
tab.close()

tab = table(gtab+"::FIELD")
field_names = tab.getcol("NAME")
tab.close()

field_in = args["field"].split(",")

try:
    ids = list(map(int, field_in))
except ValueError:
    ids = list(map(lambda a: field_names.index(a), field_in))

if not set(ids).issubset(field_ids):
    raise RuntimeError(f"Some field(s) do not have solutions after the calibration. Please refer to CASA {config.binary} logfile for further details")
