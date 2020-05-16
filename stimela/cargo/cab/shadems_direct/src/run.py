# -*- coding: future_fstrings -*-
import sys

from scabha import log, config, parameters, prun_multi, OUTPUT

errors = prun_multi([f"{config.binary} {parameters.ms} {args} --dir {OUTPUT}" for args in parameters.args])

for cmd, exc in errors:
    log.error(f"{cmd}: failed with return code {exc.returncode}")

if errors and not parameters.get('ignore_errors'):
    sys.exit(1)
