# -*- coding: future_fstrings -*-
import sys

from scabha import log, config, parameters, prun_multi, clear_junk, OUTPUT

import os
os.system("ls -l /stimela_mount")
os.system("ls -l /stimela_mount/msdir")

errors = prun_multi([f"{config.binary} {parameters.ms} {args} --dir {OUTPUT}" for args in parameters.args])

clear_junk()

for cmd, exc in errors:
    log.error(f"{cmd}: failed with return code {exc.returncode}")

if errors and not parameters.get('ignore_errors'):
    sys.exit(1)


