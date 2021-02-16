import glob
import os, os.path
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from omegaconf.omegaconf import MISSING, OmegaConf
from collections import OrderedDict
import stimela


CONFIG_FILE = os.path.expanduser("~/.config/stimela.conf")


## almost supported by omegaconf, see https://github.com/omry/omegaconf/issues/144, for now just use Any
# ListOrString = Union[str, List[str]]
ListOrString = Any

Conditional = Optional[str]

from stimela.configuratt import build_nested_config

def EmptyDictDefault():
    return field(default_factory=lambda:{})


## schema for cab parameters

class IOType(Enum):
    input  = 1
    output = 2
    mixed  = 3


@dataclass
class CabParameter:
    info: str = "parameter description"
    dtype: str = MISSING
    default:  Optional[Any] = None
    required: Optional[bool] = False
    io:       Optional[IOType] = IOType.input
    choices:  Optional[List[Any]] = ()
    internal_name: Optional[str] = ""
    positional: Optional[bool] = False
    repeat_policy: Optional[str] = MISSING
    pattern: Optional[str] = MISSING
    prefix: Optional[str] = MISSING

CabParameterSet = Dict[str, CabParameter]

## schema for a stimela image

@dataclass
class ImageBuildInfo:
    info: Optional[str] = ""
    dockerfile: Optional[str] = "Dockerfile"
    production: Optional[bool] = True          # False can be used to mark test (non-production) images 

@dataclass 
class CabManagement:        # defines common cab management behaviours
    environment: Optional[Dict[str, str]] = EmptyDictDefault()
    cleanup: Optional[Dict[str, ListOrString]]     = EmptyDictDefault()   
    wranglers: Optional[Dict[str, ListOrString]]   = EmptyDictDefault()   


@dataclass
class StimelaImage:
    name: str = MISSING
    info: str = "image description"
    images: Dict[str, ImageBuildInfo] = MISSING
    path: str = ""          # path to image definition yaml file

    # optional library of common parameter sets
    params: Dict[str, Any] = EmptyDictDefault()

    # optional library of common management settings
    management: Dict[str, CabManagement] = EmptyDictDefault()


## schema for a cab definition file

@dataclass 
class CabDefinition:
    task: str = MISSING
    info: str = MISSING
    image: str = MISSING
    msdir: Optional[bool] = False
    prefix: Optional[str] = "-"
    binary: Optional[str] = ""
    management: CabManagement = CabManagement()
    inputs: Optional[Dict[str, CabParameter]] = EmptyDictDefault()
    outputs: Optional[Dict[str, CabParameter]] = EmptyDictDefault()


## overall Stimela config schema
import stimela.backends.docker
import stimela.backends.singularity
import stimela.backends.podman

Backend = Enum("Stimela.Backend", "docker singularity podman")

@dataclass
class StimelaOptions:
    backend: Backend = "docker"
    registry: str = "quay.io"
    basename: str = "stimela/v2-"
    singularity_image_dir: str = "~/.singularity"

def DefaultDirs():
    return field(default_factory=lambda:dict(input='.', output='.'))


@dataclass
class StimelaStep:
    cab: Optional[str] = None                      # if not None, this step is a cab and this is the cab name
    recipe: Optional["StimelaRecipe"] = None       # if not None, this step is a nested recipe
    dir: Dict[str, str] = DefaultDirs()            # overrides recipe dirs, if specified
    input: Dict[str, Any] = EmptyDictDefault()     # assigns input parameters
    output: Dict[str, Any] = EmptyDictDefault()    # assigns output parameters

    _skip: Conditional = None                       # skip this step if conditional evaluates to true
    _break_on: Conditional = None                   # break out (of parent receipe) if conditional evaluates to true

#     cab: str = MISSING
#     indir:  Optional[str] = None
#     outdir: Optional[str] = None
#     msdir: Optional[str] = None
#     inputs: Dict[str, Any] = EmptyDictDefault()
# #    outputs: Optional[Dict[str, StepOutput]] = MISSING
#     info: Optional[str] = ""


@dataclass
class StimelaRecipe:
    info: str = "my recipe"
    # job_type: str = "docker"
    # sid: Optional[str] = ""
    dir: Dict[str, str] = DefaultDirs()
    var: Optional[Dict[str, Any]] = EmptyDictDefault() 
    steps: Dict[str, StimelaStep] = MISSING
    outputs: Optional[Dict[str, Any]] = MISSING  # could be a list or string


@dataclass 
class StimelaConfig:
    base: Dict[str, StimelaImage] = EmptyDictDefault()
    cab: Dict[str, CabDefinition] = MISSING
    opts: StimelaOptions = StimelaOptions()
    recipe: Optional[StimelaRecipe] = MISSING

_CONFIG_BASENAME = "stimela.conf"

# dict of config file locations to check, in order of preference
CONFIG_LOCATIONS = OrderedDict(
    local   = _CONFIG_BASENAME,
    venv    = os.environ['VIRTUAL_ENV'] and os.path.join(os.environ['VIRTUAL_ENV'], _CONFIG_BASENAME),
    user    = os.path.join(os.path.os.path.expanduser("~/.config"), _CONFIG_BASENAME)
)

# set to the config file that was actually found
CONFIG_LOADED = None

def load_config():
    stimela_dir = os.path.dirname(stimela.__file__)

    # start with empty structured config containing schema
    base_schema = OmegaConf.structured(StimelaImage) 
    cab_schema = OmegaConf.structured(CabDefinition)
    opts_schema = OmegaConf.structured(StimelaOptions)

    conf = {}

    # merge base/*/*yaml files into the config, under base.imagename
    base_configs = glob.glob(f"{stimela_dir}/cargo/base/*/*.yaml")
    conf['base'] = build_nested_config(conf, base_configs, base_schema, nameattr='name', include_path='path', section_name='base')

    # merge all cab/*/*yaml files into the config, under cab.taskname
    cab_configs = glob.glob(f"{stimela_dir}/cargo/cab/*/*.yaml")
    conf['cab'] = build_nested_config(conf, cab_configs, cab_schema, nameattr='task', section_name='cab')

    conf['opts'] = opts_schema
    # merge global config into opts
    for _, config_file in CONFIG_LOCATIONS.items():
        if config_file and os.path.exists(config_file):
            conf['opts'] = OmegaConf.merge(opts_schema, OmegaConf.load(config_file))
            global CONFIG_LOADED
            CONFIG_LOADED = config_file
            break
    
    return OmegaConf.create(conf)


    # print(conf.cab.casa_applycal.inputs)
    # print(OmegaConf.to_yaml(conf, resolve=True))
    # print(f"prefix: {conf.cab.casa_applycal.prefix} type {type(conf.cab.casa_applycal.prefix)}")


# # %%
# from omegaconf import OmegaConf
# cfg = OmegaConf.create({"foo": {"bar" : 10, "y": 11}})
# print(cfg)
# cfg.merge_with({"x":  20, "foo": {"bar": 20}})
# print(cfg)
# # %%

 
