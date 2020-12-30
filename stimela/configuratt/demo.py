import glob
import re
import os.path
import munch
import sys

import stimela

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, LiteralScalarString
from ruamel.yaml.scalarbool import ScalarBoolean
from ruamel.yaml.scalarfloat import ScalarFloat
from ruamel.yaml.scalarint import ScalarInt
from ruamel.yaml.nodes import ScalarNode
from ruamel.yaml.compat import StringIO

class MyYAML(ruamel.yaml.YAML):
    def dump(self, data, stream=None, **kw):
        to_string = False
        if stream is None:
            to_string = True
            stream = StringIO()
        ruamel.yaml.YAML.dump(self, data, stream, **kw)
        if to_string:
            return stream.getvalue()

yaml = MyYAML()

def nest_yml(input_yml, *nesting):
    """
    Given a string of YML (or open file object), converts it to YML inside a nested namespace.

    I.e. nest_yml("a: 1\nb:2", "foo", "bar") results in the following string:
    foo:
        bar:
            a: 1
            b: 2 
    """
    output = ""
    prefix = ""
    for name in nesting:
        if name:
            output += f"{prefix}{name}:\n"
        prefix += "  "
    if type(input_yml) is str:
        lines = input_yml.split("\n")
    elif hasattr(input_yml, 'readlines'):
        lines = input_yml.readlines()
    else:
        raise TypeError(f"invalid input_yml argument of type {type(input_yml)}")
    return output + "\n".join(prefix+line for line in lines)

_TYPEMAP = { str: DoubleQuotedScalarString, int: ScalarInt, bool: ScalarBoolean, float: ScalarFloat}
_RE_ANCHORS = re.compile("^[\w-]+$")

def drop_anchors(mapping, name=None):
    """Given a CommentedMap object, recursively scans through it and assigns anchors"""
    for key in list(mapping.keys()):
        value = mapping[key]
        fullname = f"{name}-{key}" if name is not None else key
        has_anchor = hasattr(value, 'anchor') and bool(value.anchor.value)
        # skip funny mapping keys (must be all digits)
        if _RE_ANCHORS.match(key):
            if not has_anchor:
                if type(value) in _TYPEMAP:
                    mapping[key] = value = _TYPEMAP[type(value)](value)
                elif value is None:
                    mapping[key] = value = LiteralScalarString("null")
                value.yaml_set_anchor(fullname, always_dump=True)
            if isinstance(value, CommentedMap):
                drop_anchors(value, fullname)
    if name is None:
        mapping.yaml_set_anchor("ROOT")

def load_nested_configs(config_dict, nesting, prior=""):
    if type(prior) is CommentedMap:
        ymldoc = yaml.dump(prior)
    elif type(prior) is str:
        ymldoc = prior
    else:
        raise TypeError(f"invalid prior argument pof type {type(prior)}")

    for name, path in config_dict.items():
        ymldoc += nest_yml(open(path), *(list(nesting) + [name]))

    open("demo.yml", "w").write(ymldoc)

    root = yaml.load(ymldoc)
    drop_anchors(root)

    return root


if __name__ == "__main__":

    stimela_dir = os.path.dirname(stimela.__file__)

    # load all base/*/*yml files into hierachy under stimela: base
    base_configs = {}    
    for path in glob.glob(f"{stimela_dir}/cargo/base/*/*.yml"):
        base_configs[os.path.basename(os.path.dirname(path))] = path

    # root_map now contains the stimele.base config
    root_map = load_nested_configs(base_configs, ("stimela", "base"))

    # load all cab/*/*yml files into hierachy under stimela: cab
    cab_configs = {}
    for path in glob.glob(f"{stimela_dir}/cargo/cab/*/*.yml"):
        cab_configs[os.path.basename(os.path.dirname(path))] = path

    # this adds the cab configs under stimela.cab, while allowing them to use aliases from stimela.base
    root_map = load_nested_configs(cab_configs, ("", "cab"), prior=root_map)

    # print the resulting config
    yaml.dump(root_map, sys.stdout)

    # munch converts nested dicts into something more nicer
    conf = munch.Munch.fromDict(root_map)

    # Munch allows syntax like this:
    print(conf.stimela.base.casa.images.keys())
    # ...and still supports the traditionally horrible old way of
    print(conf['stimela']['base']['casa']['images'].keys())


