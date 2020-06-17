# -*- coding: future_fstrings -*-
import Crasa.Crasa as crasa
from scabha import config, parameters_dict, prun

print(f"Running CASA task '{config.binary}'")

task = crasa.CasaTask(config.binary, **parameters_dict)
task.run()
