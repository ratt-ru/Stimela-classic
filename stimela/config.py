import glob
import os, os.path, time, re, logging
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from omegaconf.omegaconf import MISSING, OmegaConf
from omegaconf.errors import OmegaConfBaseException
from collections import OrderedDict
import stimela
from stimela import configuratt

from stimela.exceptions import *

CONFIG_FILE = os.path.expanduser("~/.config/stimela.conf")

from stimela.configuratt import build_nested_config

from scabha.cargo import ListOrString, EmptyDictDefault, EmptyListDefault, Parameter, Cab, CabManagement 


## schema for a stimela image

@dataclass
class ImageBuildInfo:
    info: Optional[str] = ""
    dockerfile: Optional[str] = "Dockerfile"
    production: Optional[bool] = True          # False can be used to mark test (non-production) images 


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


@dataclass 
class StimelaLogConfig(object):
    enable: bool = True                          
    dir: str = "."                               # Default directory for log files

    name: Optional[str] = "{name}"               # Initial recipe logfile, before a recipe is running. {name} {date} {time} {datetime} is substituted.
    
    # prepended to and appended after logfile name
    prefix: str = "log-"
    suffix: str = ".txt"

    # how deep to nest individual log files. 0 means one log per recipe, 1 means one per step, 2 per each substep, etc. 
    nest: int = 999                             
    
    level: str = "INFO"                          # level at which we log



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
    log: StimelaLogConfig = StimelaLogConfig()

@dataclass
class StimelaLibrary(object):
    params: Dict[str, Any] = EmptyDictDefault()
    recipes: Dict[str, Any] = EmptyDictDefault()

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


def merge_extra_config(conf, newconf):
    from stimela import logger

    if 'cabs' in newconf:
        for cab in newconf.cabs:
            if cab in conf.cabs:
                logger().warning(f"changing definition of cab '{cab}'")
    return OmegaConf.merge(conf, newconf)


StimelaConfig = None

def get_config_class():
    return StimelaConfig

def load_config(extra_configs=List[str]):
    log = stimela.logger()

    stimela_dir = os.path.dirname(stimela.__file__)
    from stimela.kitchen.recipe import Recipe, Cab

    global StimelaConfig
    @dataclass 
    class StimelaConfig:
        base: Dict[str, StimelaImage] = EmptyDictDefault()
        lib: StimelaLibrary = StimelaLibrary()
        cabs: Dict[str, Cab] = MISSING
        opts: StimelaOptions = StimelaOptions()
        vars: Dict[str, Any] = EmptyDictDefault()

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

    def _load(conf, config_file):
        global CONFIG_LOADED
        log.info(f"loading config from {config_file}")
        try:
            newconf = configuratt.load_using(config_file, conf)
            conf = merge_extra_config(conf, newconf)
            if not CONFIG_LOADED:
                CONFIG_LOADED = config_file
        except OmegaConfBaseException as exc:
            log.error(f"error reading {config_file}: {exc}")
        return conf

    # find standard config file to use
    if not any(path.startswith("=") for path in extra_configs):
        # merge global config into opts
        for _, config_file in CONFIG_LOCATIONS.items():
            if config_file and os.path.exists(config_file):
                conf = _load(conf, config_file)

    # add local configs
    for path in extra_configs:
        if path.startswith("="):
            path = path[1:]
        log.info("loading config from {path}")
        conf = _load(conf, config_file)

    if not CONFIG_LOADED:
        log.info("no configuration files, so using defaults")
    
    return OmegaConf.create(conf)



_ds = time.strftime("%Y%m%d")
_ts = time.strftime("%H%M%S")

# dictionary of standard substitutions

SUBSTITUTIONS = OmegaConf.create(dict(date=_ds, time=_ts, datetime=f"{_ds}-{_ts}"))

