# -*- coding: future_fstrings -*-
import Crasa.Crasa as crasa
from scabha import config, parameters_dict, prun
from pyrap.tables import table
import os
import numpy

print(f"Running CASA task '{config.binary}'")

save_result = parameters_dict.pop("save_result", None)

task = crasa.CasaTask(config.binary, save_result=save_result, **parameters_dict)
task.run()

gtab = parameters_dict["caltable"]
if not os.path.exists(gtab):
    raise RuntimeError(f"The gaintable was not created. Please refer to CASA {config.binary} logfile for further details")

tab = table(gtab)
field_ids = numpy.unique(tab.getcol("FIELD_ID"))
tab.close()

field_in = parameters_dict["field"].split(",")
try:
    tab = table(gtab+"::FIELD")
    field_names = tab.getcol("NAME")
    tab.close()
except RuntimeError:
    # possible new table format
    # sadly Field name and Source name columns are empty
    # will need to figure this out, but ignoring the tests for now
    tab = table(gtab)
    field_names = numpy.unique(tab.getcol("FIELD_NAME"))
    tab.close()
    pass

if field_names:
    try:
        ids = list(map(int, field_in))
    except ValueError:
        ids = list(map(lambda a: field_names.index(a), field_in))
    if not set(ids).issubset(field_ids):
        raise RuntimeError(f"Some field(s) do not have solutions after the calibration. Please refer to CASA {config.binary} logfile for further details")

