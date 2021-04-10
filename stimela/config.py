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

from stimela.configuratt import build_nested_config

def EmptyDictDefault():
    return field(default_factory=lambda:OrderedDict())

def EmptyListDefault():
    return field(default_factory=lambda:[])


@dataclass
class Parameter:
    """Parameter (of cab or recipe)"""
    info: str = ""
    # for input parameters, this flag indicates a read-write (aka input-output aka mixed-mode) parameter e.g. an MS
    writeable: bool = False
    # data type
    dtype: Optional[str] = None
    # default value. Use MANDATORY if parameter has no default, and is mandatory
    default: Optional[str] = None
    # for file-type parameters, specifies that the filename is implicitly set inside the step (i.e. not a free parameter)
    implicit: Optional[str] = None
    # for parameters of recipes, specifies that this parameter maps onto parameter(s) of constitutent step(s)
    maps_to: List[str] = EmptyListDefault()
    # optonal list of arbitrary tags, used to group parameters
    tags: List[str] = EmptyListDefault()

    # not sure this is needed? See https://github.com/ratt-ru/Stimela/discussions/698. Leaving it in for now.
    required: bool = False

    # choices for an option-type parameter (should this be List[str]?)
    choices:  Optional[List[Any]] = ()

    # inherited from Stimela 1 -- used to handle paremeters inside containers?
    # might need a re-think, but we can leave them in for now  
    alias: Optional[str] = ""
    positional: Optional[bool] = False
    repeat_policy: Optional[str] = MISSING
    pattern: Optional[str] = MISSING
    prefix: Optional[str] = MISSING

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



## overall Stimela config schema
import stimela.backends.docker
import stimela.backends.singularity
import stimela.backends.podman

Backend = Enum("Stimela.Backend", "docker singularity podman")

@dataclass
class StimelaOptions(object):
    backend: Backend = "docker"
    registry: str = "quay.io"
    basename: str = "stimela/v2-"
    singularity_image_dir: str = "~/.singularity"

@dataclass
class StimelaLibrary(object):
    params: Dict[str, Any] = EmptyDictDefault()

def DefaultDirs():
    return field(default_factory=lambda:dict(indir='.', outdir='.'))

_CONFIG_BASENAME = "stimela.conf"

# dict of config file locations to check, in order of preference
CONFIG_LOCATIONS = OrderedDict(
    local   = _CONFIG_BASENAME,
    venv    = os.environ.get('VIRTUAL_ENV', None) and os.path.join(os.environ['VIRTUAL_ENV'], _CONFIG_BASENAME),
    user    = os.path.join(os.path.os.path.expanduser("~/.config"), _CONFIG_BASENAME)
)

# set to the config file that was actually found
CONFIG_LOADED = None

def load_config(extra_configs=List[str]):
    log = stimela.logger()

    stimela_dir = os.path.dirname(stimela.__file__)
    from stimela.recipe import Recipe, Step, Cab

    @dataclass 
    class StimelaConfig:
        base: Dict[str, StimelaImage] = EmptyDictDefault()
        lib: StimelaLibrary = StimelaLibrary()
        cabs: Dict[str, Cab] = MISSING
        opts: StimelaOptions = StimelaOptions()
        recipe: Optional[Recipe] = MISSING


    # start with empty structured config containing schema
    base_schema = OmegaConf.structured(StimelaImage) 
    cab_schema = OmegaConf.structured(Cab)
    opts_schema = OmegaConf.structured(StimelaOptions)

    conf = OmegaConf.structured(StimelaConfig)

    # merge base/*/*yaml files into the config, under base.imagename
    base_configs = glob.glob(f"{stimela_dir}/cargo/base/*/*.yaml")
    conf.base = build_nested_config(conf, base_configs, base_schema, nameattr='name', include_path='path', section_name='base')

    # merge base/*/*yaml files into the config, under base.imagename
    for path in glob.glob(f"{stimela_dir}/cargo/lib/params/*.yaml"):
        name = os.path.splitext(os.path.basename(path))[0]
        conf.lib.params[name] = OmegaConf.load(path)

    # merge all cab/*/*yaml files into the config, under cab.taskname
    cab_configs = glob.glob(f"{stimela_dir}/cargo/cabs/*.yaml")
    conf.cabs = build_nested_config(conf, cab_configs, cab_schema, nameattr='name', section_name='cabs')

    conf.opts = opts_schema

    global CONFIG_LOADED

    # find standard config file to use
    if not any(path.startswith("=") for path in extra_configs):
        # merge global config into opts
        for _, config_file in CONFIG_LOCATIONS.items():
            if config_file and os.path.exists(config_file):
                log.info("loading config from {config_file}")
                conf = OmegaConf.merge(conf, OmegaConf.load(config_file))
                CONFIG_LOADED = config_file
                break

    # add local configs
    for path in extra_configs:
        if path.startswith("="):
            path = path[1:]
        log.info("loading config from {path}")
        conf = OmegaConf.merge(conf, OmegaConf.load(path))
        if not CONFIG_LOADED:
            CONFIG_LOADED = path

    if not CONFIG_LOADED:
        log.info("no configuration files, so using defaults")
    
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

 
