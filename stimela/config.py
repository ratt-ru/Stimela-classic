import glob
import os.path
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from omegaconf.omegaconf import MISSING, OmegaConf

import stimela


CONFIG_FILE = os.path.expanduser("~/.config/stimela.conf")


## almost supported by omegaconf, see https://github.com/omry/omegaconf/issues/144, for now just use Any
# ListOrString = Union[str, List[str]]
ListOrString = Any


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



@dataclass
class StimelaStep:
    cab: str = MISSING
    indir:  Optional[str] = None
    outdir: Optional[str] = None
    msdir: Optional[str] = None
    inputs: Dict[str, Any] = EmptyDictDefault()
#    outputs: Optional[Dict[str, StepOutput]] = MISSING
    info: Optional[str] = ""


@dataclass
class StimelaRecipe:
    info: str = "my recipe"
    job_type: str = "docker"
    indir: Optional[str] = ""
    outdir: Optional[str] = ""
    msdir: Optional[str] = ""
    sid: Optional[str] = ""
    var: Optional[Dict[str, Any]] = EmptyDictDefault() 
    steps: Dict[str, StimelaStep] = MISSING


@dataclass 
class StimelaConfig:
    base: Dict[str, StimelaImage] = EmptyDictDefault()
    cab: Dict[str, CabDefinition] = MISSING
    opts: StimelaOptions = StimelaOptions()
    recipe: Optional[StimelaRecipe] = MISSING


def load_config():
    stimela_dir = os.path.dirname(stimela.__file__)

    # start with empty config. Schema is imposed automatically
    conf = OmegaConf.structured(StimelaConfig)

    # merge base/*/*yaml files into the config, under base.imagename
    base_configs = glob.glob(f"{stimela_dir}/cargo/base/*/*.yaml")
    conf = build_nested_config(conf, base_configs, section_name='base', nameattr='name', include_path='path')

    # merge all cab/*/*yaml files into the config, under cab.taskname
    cab_configs = glob.glob(f"{stimela_dir}/cargo/cab/*/*.yaml")
    conf = build_nested_config(conf, cab_configs, section_name='cab', nameattr='task')

    # merge global config into opts
    if os.path.exists(CONFIG_FILE):
        opts = OmegaConf.create({'opts': OmegaConf.load(CONFIG_FILE)})
        conf = OmegaConf.merge(conf, opts)

    return conf


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

 
