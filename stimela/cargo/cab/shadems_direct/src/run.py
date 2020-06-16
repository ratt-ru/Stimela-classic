# -*- coding: future_fstrings -*-
import sys, os, os.path

from scabha import log, config, parameters, prun_multi, OUTPUT

ms = os.path.abspath(parameters.ms)
os.chdir(OUTPUT)

errors = prun_multi([f"{config.binary} {ms} {args}" for args in parameters.args])

for cmd, exc in errors:
    log.error(f"{cmd}: failed with return code {exc.returncode}")

if errors and not parameters.get('ignore_errors'):
    sys.exit(1)
