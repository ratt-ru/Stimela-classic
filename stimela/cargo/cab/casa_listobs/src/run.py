# -*- coding: future_fstrings -*-
import sys
import Crasa
import Crasa.Crasa as crasa
from scabha import config, parameters, prun

print(f"Running CASA task '{config.binary}'")

args = parameters._mapping
task = crasa.CasaTask(config.binary, **args)
task.run()
