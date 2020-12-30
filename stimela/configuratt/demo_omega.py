import glob
import re
import os.path
import munch
import sys

from omegaconf.errors import ValidationError

import stimela


from omegaconf.omegaconf import MISSING, OmegaConf
from typing import Any, List, Dict, Optional, Union
from dataclasses import dataclass, field


## this is essentially a schema for a base image definition file

ListOrString = List[str] # Union[str, List[str]]

def EmptyDictDefault():
    return field(default_factory=lambda:{})

@dataclass
class ImageBuildInfo:
    info: str
    dockerfile: Optional[str] = "Dockerfile"
    package_info: Optional[str] = ""

@dataclass 
class CabManagement:        # defines common cab management behaviours
    environment: Optional[Dict[str, str]] = EmptyDictDefault()
    cleanup: Optional[Dict[str, str]]     = EmptyDictDefault()   # should really be ListOrString here, but omegaconf doesn't support it yet (PR open)
    wranglers: Optional[Dict[str, Any]]   = EmptyDictDefault()   


@dataclass
class StimelaImage:
    name: str = MISSING
    info: str = "image description"
    images: Dict[str, ImageBuildInfo] = MISSING

    # optional library of "random" settings
    lib: Dict[str, Any] = EmptyDictDefault()

    # list of management setups that can be inherited by cabs
    management: Dict[str, CabManagement] = field(default_factory=lambda:dict(common=CabManagement()))


## this is essentially a schema for a cab definition file

@dataclass
class CabParameter:
    info: str = "parameter description"
    type: str = MISSING
    default: Any = MISSING
    choices: Optional[List[Any]] = ()

@dataclass 
class CabDefinition:
    task: str
    info: str
    image: str
    msdir: Optional[bool] = False
    prefix: Optional[str] = "-"
    binary: Optional[str] = ""
#    management: CabManagement = CabManagement()
#    inputs: Optional[Dict[str, CabParameter]] = EmptyDictDefault()
#    outputs: Optional[Dict[str, CabParameter]] = EmptyDictDefault()
    management: Optional[Dict[str, Any]] = EmptyDictDefault()
    inputs: Optional[Dict[str, Any]] = EmptyDictDefault()
    outputs: Optional[Dict[str, Any]] = EmptyDictDefault()

@dataclass 
class StimelaConfig:
    base: Dict[str, StimelaImage] = EmptyDictDefault()
    cab: Dict[str, CabDefinition] = MISSING


if __name__ == "__main__":

    stimela_dir = os.path.dirname(stimela.__file__)

    stimela_schema = OmegaConf.structured(StimelaConfig)

    base_schema = OmegaConf.structured(StimelaImage)
    # load all base/*/*yml files into hierachy under stimela: base
    base_configs = {}    
    for path in glob.glob(f"{stimela_dir}/cargo/base/*/*.yaml"):
        conf = OmegaConf.load(path)
        conf = OmegaConf.merge(base_schema, conf)
        base_configs[conf.name] = conf
    # 
    baseconf = OmegaConf.create(dict(base=base_configs))
    conf = OmegaConf.merge(StimelaConfig, baseconf)

    # load all cab/*/*yml files into hierachy under stimela: cab
    cab_schema = OmegaConf.structured(CabDefinition)
    cab_configs = {}
    for path in glob.glob(f"{stimela_dir}/cargo/cab/*/*.yaml"):
        cabconf = OmegaConf.load(path)
        cabconf1 = OmegaConf.create(dict(cab={cabconf.task: cabconf}))
        conf = OmegaConf.merge(conf, cabconf1)

#    cabconf = OmegaConf.create(dict(cab=cab_configs))

 #   rootconf = OmegaConf.merge(baseconf, cabconf)

    print(conf.cab.casa_applycal.inputs._includes[0])
    print(conf.cab.casa_applycal.management)
    print(conf.cab.casa_applycal.management._includes[0])

    print(OmegaConf.to_yaml(conf, resolve=True))


