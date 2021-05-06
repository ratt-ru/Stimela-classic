import os.path
from collections.abc import Sequence

from omegaconf.omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from omegaconf.errors import OmegaConfBaseException
from typing import Any, List, Dict, Optional, Union, Callable


def _lookup_nameseq(name_seq: List[str], source_dict: Dict):
    """Internal helper: looks up nested item ('a', 'b', 'c') in a nested dict

    Parameters
    ----------
    name_seq : List[str]
        sequence of keys to look up
    source_dict : Dict
        nested dict

    Returns
    -------
    Any
        value if found, else None
    """
    source = source_dict
    names = list(name_seq)
    while names:
        source = source.get(names.pop(0), None)
        if source is None:
            return None
    return source        


def _lookup_name(name: str, *sources: List[Dict]):
    """Internal helper: looks up a nested item ("a.b.c") in a list of dicts

    Parameters
    ----------
    name : str
        section name to look up, e.g. "a.b.c"

    Returns
    -------
    Any
        first matching item found

    Raises
    ------
    NameError
        if matching item is not found
    """
    name_seq = name.split(".")
    for source in sources:
        result = _lookup_nameseq(name_seq, source)
        if result is not None:
            return result
    raise NameError(f"unknown key {name}")


def resolve_config_refs(conf, name: str, *sources):
    """Resolves cross-references ("_use" fieds) in config object

    Parameters
    ----------
    conf : OmegaConf object
        input configuration object
    name : str
        name of this configuration section, used for messages
    *sources : OmegaConf objects
        one or more config object(s) in which to look up references

    Returns
    -------
    conf : OmegaConf object    
        This may be a new object if a _use key was resolved, or it may be the existing object

    Raises
    ------
    TypeError
        If a _use directive is malformed
    NameError
        If a _use directive names an unknown section
    """
    if isinstance(conf, DictConfig):
        merge_sections = conf.pop("_use", None)
        if merge_sections:
            if type(merge_sections) is str:
                merge_sections = [merge_sections]
            elif not isinstance(merge_sections, Sequence):
                raise TypeError(f"invalid {name}._use field of type {type(merge_sections)}")
            if len(merge_sections):
                # convert to actual sections
                merge_sections = [_lookup_name(name, *sources) for name in merge_sections]
                # merge them all
                base = merge_sections[0].copy()
                base.merge_with(*merge_sections[1:])
                base.merge_with(conf)
                conf = base
        # recurse into content
        for key, value in conf.items_ex(resolve=False):
            if isinstance(value, (DictConfig, ListConfig)):
                value1 = resolve_config_refs(value, f"{name}.{key}", *sources)
                # reassigning is expensive, so only do it if there was an actual change 
                if value1 is not value:
                    conf[key] = value1
    elif isinstance(conf, ListConfig):
        # recurse in
        for i, value in enumerate(conf._iter_ex(resolve=False)):
            if isinstance(value, (DictConfig, ListConfig)):
                value1 = resolve_config_refs(value, f"{name}[{i}]", *sources)
                if value1 is not value:
                    conf[i] = value
    return conf


def load_using(path: str, conf: DictConfig, name: Optional[str]=None, selfrefs: bool=True):
    subconf = OmegaConf.load(path)
    name = name or os.path.basename(path)
    return resolve_config_refs(subconf, name, *((conf, subconf) if selfrefs else (conf,)))


def build_nested_config(conf, filelist: List[str], schema,
                        section_name: Optional[str] = None,  
                        nameattr: Union[Callable, str, None] = None,
                        include_path: Union[None, str] = None):
    """Builds nested configuration from a set of YAML files corresponding to sub-sections

    Parameters
    ----------
    conf : OmegaConf object
        root OmegaConf object to merge content into
    filelist : List[str]
        list of subsection config files to load
    section_name : str or None
        if set, contents of files will be loaded under section_name: subsection_name. If not set, then subsection_name will be created
        directly at the root level of the config
    nameattr : Union[Callable, str, None]
        if None, subsection_name will be taken from the basename of the file. If set to a string such as 'name', will set 
        subsection_name from that field in the subsection config. If callable, will be called with the subsection config object as a single 
        argument, and must return the subsection name
    include_path : Union[None, str] 
        if set, path to each config file will be included in the section as element 'include_path'

    Returns
    -------
    OmegaConf object
        merged config with all subsections

    Raises
    ------
    NameError
        If subsection name is not resolved
    """
    section_content = {}
    for path in filelist:
        subconf = OmegaConf.load(path)
        if include_path:
            subconf[include_path] = path
        if nameattr is None:
            name = os.path.split(os.path.basename(subconf))[0]
        elif callable(nameattr):
            name = nameattr(subconf) 
        elif nameattr in subconf:
            name = subconf.get(nameattr)
        else:
            raise NameError(f"{path} does not contain a '{nameattr}' field")
        try:
            section_content[name] = OmegaConf.merge(schema, 
                resolve_config_refs(subconf, f"{section_name}.{name}" if section_name else name, conf, subconf))
        except OmegaConfBaseException as exc:
            raise RuntimeError(f"config error in {path}:\n  {exc}")

    return section_content


