from stimela import utils
import logging
import sys
import os
import textwrap

USER = os.environ['USER']

TYPES = {
    "str"   :   str,
    "float" :   float,
    "bool"  :   bool,
    "int"   :   int,
    "list"  :   list,
   }


IODEST = {
    "input"     :   "/input",
    "output"    :   "/home/{}/output".format(USER),
    "msfile"    :   "/home/{}/msdir".format(USER),
}


class Parameter(object):
    def __init__(self, name, dtype, info, 
        default=False, 
        required=False,
        choices=None, 
        io=None,
        mapping=None,
        #delimiter=None, 
        check_io=True):

        self.name = name
        self.io = io
        #self.delimiter = delimiter
        
        if not hasattr(dtype,'__iter__'):
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
        if self.choices and value not in self.choices:
            raise ValueError("Parameter '{0}', can only be either of {1}".format(self.name, self.choices))

        for item in self.dtype:
            if isinstance(item, tuple):
                l,t = item
                if t=="file":
                    return True
                if isinstance(value, t):
                    return True
                elif isinstance(value, list):
                    if value == []:
                        return True
                    elif isinstance(value[0], tuple([t]+[int] if t is float else [t])):
                        return True
            elif item is "file":
                return True
            elif isinstance(value, tuple([item]+[int] if item is float else [item])):
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
        tag=None,
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
            self.tag = cab["tag"]
            if cab["msdir"]:
                self.msdir = msdir
            self.description = cab["description"]
            self.prefix = cab["prefix"]
            parameters0 = cab["parameters"]
            self.parameters = []
            
            import sys
            for param in parameters0:
                default = param.get("default", param.get("value", None))
                addme = Parameter(name=param["name"],
                        dtype=param["dtype"],
                        io=param.get("io", None),
                        info=param.get("info", None) or "No documentation. Bad! Very bad...",
                        default=default,
                        mapping=param.get("mapping", None),
                        #delimiter=param.get("delimiter", None),
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
            self.tag = tag

        
    def display(self, header=False):
        rows, cols = os.popen('stty size', 'r').read().split()
        lines = textwrap.wrap(self.description, int(cols)*3/4)
        print("Cab      {0}".format(self.task))
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
            for i,_type in enumerate(param.dtype):
                if isinstance(_type, tuple):
                    _name = "list:{}".format("file" if _type[1]=="file" else _type[1].__name__)
                else:
                    _name = "file" if _type=="file" else _type.__name__
                _types += "{}".format(_name) if i==0 else "/{}".format(_name)

            lines = textwrap.wrap(param.info, int(cols)*3/4)

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
        for item in "task base binary msdir description prefix tag".split():
            if item == 'msdir':
                conf[item] = getattr(self, item, False)
            else:
                conf[item] = getattr(self, item)
        
        conf["parameters"] = []
        for param in self.parameters:
        
            if isinstance(param.dtype[0], tuple):
                if not hasattr(param.value, '__iter__') and param.value is not None:
                    param.value = [param.value]

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
                    "value"     :   param.default if param.value is None else param.value
                })
        return conf


    def update(self, options, saveconf):
        required = filter(lambda a: a.required, self.parameters)
        for param0 in required:
            if not options.has_key(param0.name) and not options.has_key(param0.mapping):
                raise RuntimeError("Parameter {} is required but has not been specified".format(param0.name))

        self.log.info("Validating parameters...       CAB = {0}".format(self.task))
        for name,value in options.iteritems():
            found = False
            for param in self.parameters:
                if name in [param.name, param.mapping]:
                    found = True
                    if param.io:
                        if value is None:
                            continue
                        param.validate(value)
                        param.value = []
                        if not hasattr(value, "__iter__"):
                            value = [value]
                        for _value in value:
                            val = _value.split(":")
                            if len(val)==2:
                                if val[1] not in IODEST.keys():
                                    raise IOError('The location \'{0}\' specified for parameter \'{1}\', is unknown. Choices are {2}'.format(val[1], param.name, IODEST.keys()))
                                self.log.info("Location of '{0}' was specified as '{1}'. Will overide default.".format(param.name, val[1]))
                                _value = val[0]
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
                                param.value.append("{0}/{1}".format(IODEST[location], _value))
                        if len(param.value)==1:
                            param.value = param.value[0]
                        
                    else:
                        self.log.debug("Validating paramter {}".format(param.name))
                        param.validate(value)
                        param.value = value
            if not found:
                raise RuntimeError("Parameter {0} is unknown. Run 'stimela cabs -i {1}' to get help on this cab".format(name, self.task))
        conf = {}
        conf.update(self.toDict())
        utils.writeJson(saveconf, conf)
        self.log.info("Parameters validated and saved. Parameter file is: {}".format(saveconf))
