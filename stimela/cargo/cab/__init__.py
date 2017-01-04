from stimela import utils
import logging
import sys
import os
import textwrap



TYPES = {
    "str"   :   str,
    "float" :   float,
    "bool"  :   bool,
    "int"   :   int,
   }

IODEST = {
    "input"     :   "/input",
    "output"    :   "$HOME/output",
    "msfile"    :   "$HOME/output/msdir",
}

class Parameter(object):
    def __init__(self, name, dtype, info, 
        default=False, 
        required=False,
        choices=None, 
        io=None,
        mapping=None,
        delimeter=None, 
        check_io=True):

        self.name = name
        self.io = io
        self.delimeter = delimeter
        
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

        self.value = None

    def validate(self, value):
        for item in self.dtype:
            if isinstance(item, tuple):
                l,t = item
                if t=="file":
                    return True
                if isinstance(value, t):
                    return True
            elif isinstance(value, tuple(TYPES.values())):
                return True
        raise TypeError("Expecting any of types {0} for parameter '{1}', but got '{2}'".format( self.dtype, self.name, type(value).__name__))


    def get_type(self, dtype):

        def _type(a):
            if a == "file":
                if self.io not in ["input", "output", "msfile"]:
                    raise TypeError("io '{0}' for parameter '{1}' not understood. Please specify 'io' as either 'input', 'output' or 'msfile'".format(self.io, self.name))
                return "file"
            else:
                return TYPES[a]

        if dtype.startswith("list:"):
            val = dtype.split(":")
            if self.delimeter is None:
                raise RuntimeError("The parameter {0} is to be supplied as list but no delimter has been provided. Please add a 'delimeter' field to the cab parameter file.".format(self.name))
            if len(val) != 2:
                raise TypeError("The type of '{0}' could not validate. Specify list types as \"list:dtype\" where dtype is normal type")
            ttype = val[1]

            return (list, _type(ttype))
        else:
            return _type(dtype)
            


class CabDefinition(object):
    def __init__(self, 
        indir=None,  # input directory
        outdir=None, # output directory
        msdir=None,  # MS directory
        parameter_file=None,
        task=None,
        base=None,
        binary=None,
        description=None,
        prefix=None, loglevel='INFO',
        parameters=[]):

        logging.basicConfig(level=getattr(logging, loglevel))
        self.log = logging
        self.indir = indir
        self.outdir = outdir

        if parameter_file:
            cab = utils.readJson(parameter_file)
            self.task = cab["task"]
            self.base = cab["base"]
            self.binary = cab["binary"]
            if cab["msdir"]:
                self.msdir = msdir
            self.description = cab["description"]
            self.prefix = cab["prefix"]
            parameters0 = cab["parameters"]
            self.parameters = []

            for param in parameters0:
                default = param.get("default", param.get("value", None))
                addme = Parameter(name=param["name"],
                        dtype=param["dtype"],
                        io=param.get("io", None),
                        info=param.get("info", "No documentation. Bad! Very bad..."),
                        default=default,
                        mapping=param.get("mapping", None),
                        delimeter=param.get("delimeter", None),
                        required=param.get("required", False),
                        choices=param.get("choices", False),
                        check_io=param.get("check_io", True))
                self.parameters.append(addme)

        else:
            self.task = task
            self.base = base
            self.binary = binary
            self.prefix = prefix
            self.parameters = parameters
            self.description = description
            self.msdir = msdir

        
    def display(self):
        print("{}\n \n".format(self.description))
        print("Stimela Cab      {0}".format(self.task))
        print("Base Image       {0}".format(self.base))
        print("\n")

        print("Parameters:")
        rows, cols = os.popen('stty size', 'r').read().split()
        for param in self.parameters:
            
            _types = ""
            for i,_type in enumerate(param.dtype):
                if isinstance(_type, tuple):
                    _name = "list:{}".format("file" if _type[1]=="file" else _type[1].__name__)
                else:
                    _name = "file" if _type=="file" else _type.__name__
                _types += "{}".format(_name) if i==0 else "/{}".format(_name)

            lines = textwrap.wrap(param.info, int(cols)/2)

            print("  Name         {}{}".format(param.name, "/{}".format(param.mapping) if param.mapping else ""))
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
        for item in "task base binary msdir description prefix".split():
            conf[item] = getattr(self, item)
        
        conf["parameters"] = []
        for param in self.parameters:
            _value = param.value or param.default
        
            if isinstance(param.dtype[0], tuple):
                if not isinstance(_value, (list, tuple)):
                    _value = [_value]
                value = param.delimeter.join(map(str, _value))
            else:
                value = _value

            _types = ""
            for i,_type in enumerate(param.dtype):
                if isinstance(_type, tuple):
                    _name = "list:{}".format("file" if _type[1]=="file" else _type[1].__name__)
                else:
                    _name = "file" if _type=="file" else _type.__name__
                _types += "{}".format(_name) if i==0 else "/{}".format(_name)

            conf["parameters"].append(
                {
                    "name"      :   param.mapping or param.name,
                    "dtype"     :   _types,
                    "info"      :   param.info,
                    "required"  :   param.required,
                    "check_io"  :   param.check_io,
                    "value"     :   value,
                })
        return conf


    def update(self, options, saveconf):
        required = filter(lambda a: a.required, self.parameters)
        for param0 in required:
            if param0.name not in options.keys():
                raise RuntimeError("Parameter {} is required but has not been specified".format(param0.name))

        self.log.info("Validating parameters...")
        for name,value in options.iteritems():
            for param in self.parameters:
                if param.name == name:
                    if param.io:
                        param.validate(value)
                        param.value = []
                        if not hasattr(value, "__iter__"):
                            value = [value]
                        for _value in value:
                            val = _value.split(":")
                            if len(val)==2:
                                self.log.info("Location of '{0}' was specified as '{1}'. Will overide default.".format(param.name, val[1]))
                                value = val[0]
                                location = val[1]
                            else:
                                location = param.io

                            if location in ["input", "msfile"]:
                                if location == "input" and self.indir is None:
                                    raise IOError("You have specified input files, but have not specified an input folder")
                                if location == "msfile" and self.msdir is None:
                                    raise IOError("You have specified MS files, but have not specified an MS folder")

                                path = "{0}/{1}".format(self.indir if location=="input" else self.msdir, _value)
                                if param.check_io and not os.path.exists(path):
                                    raise IOError("File '{0}' for parameter '{1}' could not be located at '{2}'.".format(_value, param.name, path))
                                param.value.append ("{0}/{1}".format(IODEST[location], _value))
                            else:
                                if self.outdir is None:
                                    raise IOError("You have specified output files, but have not specified an output folder")
                                param.value.append("{0}/{1}".format(IODEST[location], value_))
                        if len(param.value)==1:
                            param.value = param.value[0]
                        
                    elif param.validate(value):
                        self.log.debug("Validating paramter {}".format(param.name))
                        param.value = value

        conf = {}
        conf.update(self.toDict())
        utils.writeJson(saveconf, conf)
        self.log.info("Parameters validated and saved. Parameter file is: {}".format(saveconf))
