# -*- coding: future_fstrings -*-
import Crasa.Crasa as crasa
from scabha import config, parameters_dict, prun

print(f"Running CASA task '{config.binary}'")

save_result = parameters_dict.pop("save_result", None)

task = crasa.CasaTask(config.binary, save_result=save_result, **parameters_dict)
task.run()
