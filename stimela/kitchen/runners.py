import shlex

from scabha.cargo import Cab
from stimela import logger
from stimela.utils.xrun_poll import xrun
from stimela.exceptions import StimelaCabRuntimeError


def run_cab(cab: Cab, log=None):
    log = log or logger()
    if cab.image:
        raise RuntimeError("container runner not yet implemented")
    else:
        return run_cab_natively(cab, log=log)



def run_cab_natively(cab: Cab, log):
    import scabha
    from scabha import proc_utils

    args, venv = cab.build_command_line()

    command_name = args[0]

    if venv:
        args = ["/bin/bash", "--rcfile", f"{venv}/bin/activate", "-c", " ".join(shlex.quote(arg) for arg in args)]

    log.debug(f"command line is {args}")
    
    cab.reset_runtime_status()

    retcode = xrun(args[0], args[1:], shell=False, log=log, 
                output_wrangler=cab.apply_output_wranglers, 
                return_errcode=True, command_name=command_name)

    # if retcode is not 0, and cab didn't declare itself a success,
    if retcode:
        if not cab.runtime_status:
            raise StimelaCabRuntimeError(f"{command_name} returned non-zero exit status {retcode}", log=log)
    else:
        if cab.runtime_status is False:
            raise StimelaCabRuntimeError(f"{command_name} was marked as failed based on its output", log=log)

    return retcode
