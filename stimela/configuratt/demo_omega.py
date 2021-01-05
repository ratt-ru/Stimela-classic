import glob
import re
import os.path
from stimela.docker import build
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
    msfile = 4


@dataclass
class CabParameter:
    info: str = "parameter description"
    type: str = MISSING
    default:  Optional[Any] = MISSING
    required: Optional[bool] = False
    io:       Optional[IOType] = IOType.input
    choices:  Optional[List[Any]] = ()
    internal_name: Optional[str] = ""

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

    # optional library of common parameter sets
    params: Dict[str, Any] = EmptyDictDefault()

    # optional library of common management settings
    management: Dict[str, CabManagement] = EmptyDictDefault()


## schema for a cab definition file

@dataclass 
class CabDefinition:
    task: str
    info: str
    image: str
    msdir: Optional[bool] = False
    prefix: Optional[str] = "-"
    binary: Optional[str] = ""
    management: CabManagement = CabManagement()
    inputs: Optional[Dict[str, CabParameter]] = EmptyDictDefault()
    outputs: Optional[Dict[str, CabParameter]] = EmptyDictDefault()

@dataclass 
class StimelaConfig:
    base: Dict[str, StimelaImage] = EmptyDictDefault()
    cab: Dict[str, CabDefinition] = MISSING



if __name__ == "__main__":

    stimela_dir = os.path.dirname(stimela.__file__)

    # start with empty config. Schema is imposed automatically
    conf = OmegaConf.structured(StimelaConfig)

    # merge base/*/*yaml files into the config, under base.imagename
    base_configs = glob.glob(f"{stimela_dir}/cargo/base/*/*.yaml")
    conf = build_nested_config(conf, base_configs, section_name='base', nameattr='name')

    # merge all cab/*/*yml files into the config, under cab.taskname
    cab_configs = glob.glob(f"{stimela_dir}/cargo/cab/*/*.yaml")
    conf = build_nested_config(conf, cab_configs, section_name='cab', nameattr='task')

    print(conf.cab.casa_applycal.inputs)
    print(OmegaConf.to_yaml(conf, resolve=True))
    print(f"prefix: {conf.cab.casa_applycal.prefix} type {type(conf.cab.casa_applycal.prefix)}")


# # %%
# from omegaconf import OmegaConf
# cfg = OmegaConf.create({"foo": {"bar" : 10, "y": 11}})
# print(cfg)
# cfg.merge_with({"x":  20, "foo": {"bar": 20}})
# print(cfg)
# # %%