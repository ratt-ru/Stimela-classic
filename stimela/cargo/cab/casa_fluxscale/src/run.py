# -*- coding: future_fstrings -*-
import Crasa.Crasa as crasa
from scabha import config, parameters_dict, prun
import os

print(f"Running CASA task '{config.binary}'")

save_result = parameters_dict.pop("save_result", None)
overwrite = parameters_dict.pop("overwrite", False)
fluxtable = parameters_dict['fluxtable']
if overwrite:
    os.system(f"rm -fr {fluxtable}")

task = crasa.CasaTask(config.binary, save_result=save_result, **parameters_dict)
task.run()
