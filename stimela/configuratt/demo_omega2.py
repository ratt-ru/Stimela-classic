import glob
import re
import os.path
import munch
import sys
from collections.abc import Sequence

from omegaconf.errors import ValidationError

import stimela


from omegaconf.omegaconf import MISSING, OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field

@dataclass
class FlagWorker:
    enable: bool = False
    field: Enum("target", 'target calibrators') = "calibrators"
    label_in: Optional[str] = ""
    calfields: str = ""
    
    @dataclass 
    class RewindFlags:
        enable: bool = False
        mode: Enum('rewind_flags_mode', 'reset_worker rewind_to_version') = 'reset_worker'
        version: str = "auto"

    rewind_flags: RewindFlags = RewindFlags()
    
    # = RewindFlags()

FlagWorker_doc = dict(
    enable = "Execute the flag worker.",
    field = """Fields that should be flagged. It can be set to either 'target' or 'calibrators' 
            (i.e., all calibrators) as defined in the obsconf worker. Note that this selection is ignored -- i.e., 
            all fields in the selected .MS file(s) are flagged -- in the flagging step 'flag_mask' (see below). If a 
            user wants to only flag a subset of the calibrators the selection can be further refined using 'calfields' below. 
            The value of 'field' is also used to compose the name of the .MS file(s) that should be flagged, as explained in 
            'label_in' below.""",
    label_in = """This label is added to the input .MS file(s) name, given in the getdata worker, to define the name of the 
            .MS file(s) that should be flagged. These are <input>_<label>.ms if 'field' (see above) is set to 'calibrators', or 
            <input>-<target>_<label>.ms if 'field' is set to 'target' (with one .MS file for each target in the input .MS). If empty, 
            the original .MS is flagged with the field selection explained in 'field' above.""",
    calfields = """If 'field' above is set to 'calibrators', users can specify here what subset of calibrators to process. 
            This should be a comma-separated list of 'xcal' ,'bpcal', 'gcal' and/or 'fcal', which were all set by the obsconf worker. 
            Alternatively, 'auto' selects all calibrators.""",
    rewind_flags = "Rewind flags to specified version.",
    rewind_flags_doc = dict(
          enable = "Enable this segment",
          mode =  """If mode = 'reset_worker' rewind to the flag version before this worker if it exists, or continue if it does not exist; 
                  if mode = 'rewind_to_version' rewind to the flag version given by 'version' below.""",
          version = """Flag version to rewind to. If set to 'auto' it will rewind to the version prefix_workername_before, where 'prefix' is 
                    set in the 'general' worker, and 'workername' is the name of this worker including the suffix '__X' if it is a repeated 
                    instance of this worker in the configuration file. Note that all flag versions that had been saved after this version will 
                    be deleted."""
    )
)


if __name__ == "__main__":

    # Load default config & schema
    conf = OmegaConf.structured(FlagWorker)

    # load custom config from string (alternative: OmegaConf.load(ymlfile))
    conffile = OmegaConf.create("""
    enable: true
    field: calibrators
    rewind_flags:
        enable: true
        mode: rewind_to_version
    """)
 
    # this overwrites the default config with 'conffile', and checks the schema
    conf = OmegaConf.merge(conf, conffile)

    print(OmegaConf.to_yaml(conf, resolve=True))
    print(f"rewind_flags.version: {conf.rewind_flags.version}")
    print(f"rewind_flags.version: {conf['rewind_flags']['version']}")


