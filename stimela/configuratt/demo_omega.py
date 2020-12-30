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
    management: CabManagement = CabManagement()


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
    management: CabManagement = CabManagement()
    inputs: Optional[Dict[str, Any]] = EmptyDictDefault()
    outputs: Optional[Dict[str, Any]] = EmptyDictDefault()

@dataclass 
class StimelaConfig:
    base: Dict[str, StimelaImage] = EmptyDictDefault()
    cab: Dict[str, CabDefinition] = MISSING


def lookup_nameseq(name_seq, source_dict):
    source = source_dict
    names = list(name_seq)
    while names:
        source = source.get(names.pop(0), None)
        if source is None:
            return None
    return source        

def lookup_name(name, *sources):
    name_seq = name.split(".")
    for source in sources:
        result = lookup_nameseq(name_seq, source)
        if result is not None:
            return result
    raise NameError(f"unknown key {name}")


def resolve_merges(conf, name, *sources):
    if isinstance(conf, DictConfig):
        merge_sections = conf.pop("_merge", None)
        if merge_sections:
            if type(merge_sections) is str:
                merge_sections = [merge_sections]
            elif not isinstance(merge_sections, Sequence):
                raise TypeError(f"invalid {name}._merge field of type {type(merge_sections)}")
            if not len(merge_sections):
                raise TypeError(f"invalid {name}._merge field of length 0")
            # convert to actual sections
            merge_sections = [lookup_name(name, *sources) for name in merge_sections]
            # merge them all
            base = merge_sections[0].copy()
            base.merge_with(*merge_sections[1:])
            base.merge_with(conf)
            conf = base
        # recurse into content
        for key, value in conf.items_ex(resolve=False):
            conf[key] = resolve_merges(value, f"{name}.{key}", *sources)
    elif isinstance(conf, ListConfig):
        # recurse in
        for i, value in enumerate(conf._iter_ex(resolve=False)):
            conf[i] = resolve_merges(value, f"{name}[{i}]", *sources)
    return conf

if __name__ == "__main__":

    stimela_dir = os.path.dirname(stimela.__file__)

    # start with empty config. Schema is imposed automatically
    conf = OmegaConf.structured(StimelaConfig)

    # merge base/*/*yaml files into the config one by one, under base[imagename]
    for path in glob.glob(f"{stimela_dir}/cargo/base/*/*.yaml"):
        baseconf = OmegaConf.load(path)
        baseconf1 = OmegaConf.create(dict(base={baseconf.name: baseconf}))
        conf = OmegaConf.merge(conf, baseconf1)

    # merge all cab/*/*yml files into the config one by one, under cab[taskname]
    for path in glob.glob(f"{stimela_dir}/cargo/cab/*/*.yaml"):
        cabconf = OmegaConf.load(path)
        cabconf = resolve_merges(cabconf, "", conf, cabconf)
        cabconf1 = OmegaConf.create(dict(cab={cabconf.task: cabconf}))
        conf = OmegaConf.merge(conf, cabconf1)

#    cabconf = OmegaConf.create(dict(cab=cab_configs))

 #   rootconf = OmegaConf.merge(baseconf, cabconf)

    print(conf.cab.casa_applycal.inputs)

    print(OmegaConf.to_yaml(conf, resolve=True))


# # %%
# from omegaconf import OmegaConf
# cfg = OmegaConf.create({"foo": {"bar" : 10}})
# cfg.foo.merge_with({"x":  20, "bar": 20})
# print(cfg)
# # %%