# -*- coding: future_fstrings -*-
import stimela
from stimela import utils, recipe
import logging
import os
import sys
import textwrap
from stimela.pathformatter import pathformatter, placeholder
from stimela.exceptions import *
import time

TYPES = {
    "str":   str,
    "float":   float,
    "bool":   bool,
    "int":   int,
    "list":   list,
}

__vol = {
        "home" : "/stimela_home",
        "mount": "/stimela_mount",
        }

USER_HOME = os.environ["HOME"]

for item in list(__vol.keys()):
    val = __vol[item]
    while os.path.exists(val):
        __timestamp = str(time.time()).replace(".", "")
        val = "{0:s}-{1:s}".format(val.split("-")[0], __timestamp)
    __vol[item] = val

HOME = __vol["home"]
MOUNT = __vol["mount"]

IODEST = { 
        "input": f"{MOUNT}/input",
        "output": f"{MOUNT}/output",
        "msfile": f"{MOUNT}/msdir",
        "tmp": f"{MOUNT}/output/tmp",
    }  

class Parameter(object):
    def __init__(self, name, dtype, info,
                 default=False,
                 required=False,
                 choices=None,
                 io=None,
                 mapping=None,
                 check_io=True,
                 deprecated=False,
                 positional=False):

        self.name = name
        self.io = io

        if not isinstance(dtype, (list, tuple)):
            dtype = [dtype]
        self.dtype = []
        for item in dtype:
            tmp = self.get_type(item)
            self.dtype.append(tmp)

        self.info = info
        self.default = default
        self.required = required
        self.choices = choices or []
        self.mapping = mapping
        self.check_io = check_io
        self.deprecated = deprecated
        self.positional = positional

        self.value = None

    def __iter__(self):
       for x in ["info", "default", "positional", "required", "choices", "mapping",
                 "check_io", "value", "name", "io", "dtype"]:
          yield x

    def __getitem__(self, v):
        return getattr(self, v)

    def validate(self, value):
        if self.choices and value not in self.choices:
            raise StimelaCabParameterError("Parameter '{0}', can only be either of {1}".format(
                self.name, self.choices))

        for item in self.dtype:
            if isinstance(item, tuple):
                l, t = item
                if t == "file":
                    return True
                if isinstance(value, t):
                    return True
                elif isinstance(value, list):
                    types = (t,int) if t is float else (t,)      # float permits ints as well
                    if all(isinstance(x, types) for x in value): # check that all elements are of permitted type
                        return True
            elif item == "file":
                return True
            elif isinstance(value, tuple([item]+[int] if item is float else [item])):
                return True
        raise StimelaCabParameterError("Expecting any of types {0} for parameter '{1}', but got '{2}'".format(
            self.dtype, self.name, type(value).__name__))

    def get_type(self, dtype):

        def _type(a):
            if a == "file":
                if self.io not in ["input", "output", "msfile"]:
                    raise StimelaCabParameterError("io '{0}' for parameter '{1}' not understood. Please specify 'io' as either 'input', 'output' or 'msfile'".format(
                        self.io, self.name))
                return "file"
            else:
                return TYPES[a]

        if dtype.startswith("list:"):
            val = dtype.split(":")
            if len(val) != 2:
                raise StimelaCabParameterError(
                    "The type of '{0}' could not validate. Specify list types as \"list:dtype\" where dtype is normal type")
            ttype = val[1]

            return (list, _type(ttype))
        else:
            return _type(dtype)


class CabDefinition(object):
    def __init__(self,
                 indir=None,  # input directory
                 outdir=None,  # output directory
                 msdir=None,  # MS directory
                 parameter_file=None,
                 task=None,
                 base=None,
                 binary=None,
                 description=None,
                 tag=[],
                 prefix=None,
                 parameters=[],
                 version=[], 
                 junk=[]):

        self.indir = indir
        self.outdir = outdir


        if parameter_file:
            cab = utils.readJson(parameter_file)
            if not isinstance(cab["tag"], list):
                tag = [cab["tag"]]
                version = [cab.get("version", "x.x.x")]
            else:
                tag = cab["tag"]
                version = cab["version"]

            self.task = cab["task"]
            self.base = cab["base"]
            self.binary = cab["binary"]
            self.tag = tag
            self.junk = cab.get("junk", [])
            self.wranglers = cab.get("wranglers", [])
            self.version = version
            if cab["msdir"]:
                self.msdir = msdir
            else:
                self.msdir = None
            self.description = cab["description"]
            self.prefix = cab["prefix"]
            parameters0 = cab["parameters"]
            self.parameters = []

            for param in parameters0:
                default = param.get("default", param.get("value", None))
                addme = Parameter(name=param["name"],
                                  dtype=param["dtype"],
                                  io=param.get("io", None),
                                  info=param.get(
                                      "info", None) or "No documentation. Bad! Very bad...",
                                  default=default,
                                  mapping=param.get("mapping", None),
                                  required=param.get("required", False),
                                  positional=param.get("positional", False),
                                  choices=param.get("choices", False),
                                  check_io=param.get("check_io", True),
                                  deprecated=param.get("deprecated", False))
                self.parameters.append(addme)

        else:
            self.task = task
            self.base = base
            self.binary = binary
            self.prefix = prefix
            self.parameters = parameters
            self.description = description
            self.msdir = msdir
            self.tag = tag
            self.version = version
            self.junk = []
            self.wranglers = []

        self.log = stimela.logger()

    def __str__(self):
        res = ""
        res += "Cab definition for {}\n".format(self.task)
        for b in ["base", "binary", "prefix", "description", "tag", "version", "junk", "wranglers"]:
            res += "\t {}: {}\n".format(b, getattr(self, b))
        res += "\t Parameters:\n"
        for p in self.parameters:
            res += "\t\t {}:\n".format(p.name)
            for k in p:
                res += "\t\t\t {}: {}\n".format(k, str(p[k]))
        return res

    def display(self, header=False):
        rows, cols = os.popen('stty size', 'r').read().split()
        lines = textwrap.wrap(self.description, int(cols)*3/4)
        print("Cab      {0}  version {1}".format(self.task, self.version))
        print("Info     {}".format(lines[0]))
        for line in lines[1:]:
            print("         {}".format(line))
        if header:
            print(" ")
            return

        print("Base Image       {0}:{1}".format(self.base, self.tag))
        print("\n")

        print("Parameters:")
        rows, cols = os.popen('stty size', 'r').read().split()
        for param in self.parameters:

            _types = ""
            for i, _type in enumerate(param.dtype):
                if isinstance(_type, tuple):
                    _name = "list:{}".format(
                        "file" if _type[1] == "file" else _type[1].__name__)
                else:
                    _name = "file" if _type == "file" else _type.__name__
                _types += "{}".format(_name) if i == 0 else "/{}".format(_name)

            lines = textwrap.wrap(param.info, int(cols)*3/4)

            print("  Name         {}{}".format(param.name,
                                               "/{}".format(param.mapping) if param.mapping else ""))
            print("  Description  {}".format(lines[0]))
            for line in lines[1:]:
                print("               {}".format(line))
            print("  Type         {}".format(_types))
            print("  Default      {}".format(param.default))
            if param.choices:
                print("  Choices      {}".format(param.choices))
            print(" ")

    def toDict(self):
        conf = {}
        for item in "task base binary msdir description prefix tag version junk wranglers".split():
            if item == 'msdir':
                conf[item] = getattr(self, item, False)
            else:
                conf[item] = getattr(self, item)

        conf["parameters"] = []
        for param in self.parameters:

            if isinstance(param.dtype[0], tuple):
                if not isinstance(param.value, (list, tuple)) and param.value is not None:
                    param.value = [param.value]

            _types = ""
            for i, _type in enumerate(param.dtype):
                if isinstance(_type, tuple):
                    _name = "list:{}".format(
                        "file" if _type[1] == "file" else _type[1].__name__)
                else:
                    _name = "file" if _type == "file" else _type.__name__
                _types += "{}".format(_name) if i == 0 else "/{}".format(_name)

            conf["parameters"].append(
                {
                    "name":   param.mapping or param.name,
                    "dtype":   _types,
                    "info":   param.info,
                    "required":   param.required,
                    "positional":   param.positional,
                    "check_io":   param.check_io,
                    "value":   param.default if param.value is None else param.value
                })
        return conf

    def update(self, options, saveconf, tag=None):
        required = filter(lambda a: a.required, self.parameters)
        tag = tag or self.tag
        for param0 in required:
            if param0.name not in options.keys() and param0.mapping not in options.keys():
                raise StimelaCabParameterError(
                    "Parameter {} is required but has not been specified".format(param0.name))
        self.log.info(f"Validating parameters for cab {self.task} ({self.base}:{tag})")

        for name, value in options.items():
            found = False
            for param in self.parameters:
                if name in [param.name, param.mapping]:
                    found = True
                    if param.deprecated:
                        self.log.warning(f"Parameter {name} for cab {self.task} is deprecated, and will be removed in a future release")
                    if param.io:
                        if value is None:
                            continue
                        param.validate(value)
                        param.value = []
                        if not isinstance(value, (list, tuple)):
                            value = [value]
                        for _value in value:
                            if isinstance(_value, pathformatter):
                                if param.check_io:
                                    raise StimelaCabParameterError("Pathformatters cannot be used on io parameters where io has to be checked")
                                joinlist = _value() # construct placeholder list
                                joined_str = ""
                                for p in joinlist:
                                    if not isinstance(p, placeholder):
                                        joined_str += p
                                    else:
                                        if p() not in IODEST.keys():
                                            raise StimelaCabParameterError('The location \'{0}\' specified for parameter \'{1}\', is unknown. Choices are {2}'.format(
                                                p(), param.name, IODEST.keys()))
                                        location = p()
                                        if location in ["input", "msfile"]:
                                            if location == "input" and self.indir is None:
                                                raise StimelaCabParameterError(
                                                    "You have specified input files, but have not specified an input folder")
                                            if location == "msfile" and self.msdir is None:
                                                raise StimelaCabParameterError(
                                                    "You have specified MS files, but have not specified an MS folder")

                                            joined_str += "{0}/".format(IODEST[location])
                                        else:
                                            if self.outdir is None:
                                                raise StimelaCabParameterError(
                                                    "You have specified output files, but have not specified an output folder")
                                            joined_str += "{0}/".format(IODEST[location])

                                param.value.append(joined_str)
                            elif isinstance(_value, str):
                                val = _value.split(":")
                                if len(val) == 2:
                                    if val[1] not in IODEST.keys():
                                        raise StimelaCabParameterError('The location \'{0}\' specified for parameter \'{1}\', is unknown. Choices are {2}'.format(
                                            val[1], param.name, IODEST.keys()))
                                    self.log.info("Location of '{0}' was specified as '{1}'. Will overide default.".format(
                                        param.name, val[1]))
                                    _value = val[0]
                                    location = val[1]
                                else:
                                    location = param.io

                                if location in ["input", "msfile"]:
                                    if location == "input" and self.indir is None:
                                        raise StimelaCabParameterError(
                                            "You have specified input files, but have not specified an input folder")
                                    if location == "msfile" and self.msdir is None:
                                        raise StimelaCabParameterError(
                                            "You have specified MS files, but have not specified an MS folder")

                                    path = "{0}/{1}".format(self.indir if location ==
                                                            "input" else self.msdir, _value)
                                    if param.check_io and not os.path.exists(path):
                                        raise StimelaCabParameterError("File '{0}' for parameter '{1}' could not be located at '{2}'.".format(
                                            _value, param.name, path))
                                    param.value.append(
                                        "{0}/{1}".format(IODEST[location], _value))
                                else:
                                    if self.outdir is None:
                                        raise StimelaCabParameterError(
                                            "You have specified output files, but have not specified an output folder")
                                    param.value.append(
                                        "{0}/{1}".format(IODEST[location], _value))
                            else:
                                raise StimelaCabParameterError("io parameter must either be a pathformatter object or a string")
                        if len(param.value) == 1:
                            param.value = param.value[0]

                    else: # not io type
                        if isinstance(value, pathformatter):
                            raise StimelaCabParameterError("Path formatter type specified, but {} is not io".format(param.name))

                        self.log.debug(
                            "Validating parameter {}".format(param.name))
                        param.validate(value)
                        param.value = value
            if not found:
                raise StimelaCabParameterError(
                    "Parameter {0} is unknown. Run 'stimela cabs -i {1}' to get help on this cab".format(name, self.task))
        conf = {}
        conf.update(self.toDict())
        utils.writeJson(saveconf, conf)
        self.log.info(f"Parameters validated and saved to {saveconf}")
