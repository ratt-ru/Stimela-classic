from stimela import utils
import logging
import sys
import os

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
        io=None):

        self.name = name
        if dtype.startswith("list"):
            self.dtype = (list, TYPES[dtype.split(":")[-1]])
        elif dtype=="file":
            if io not in ["input", "output", "msfile"]:
                raise TypeError("File type '{0}' for parameter '{1}' not understood. Please specify 'io' as either 'input', 'output' or 'msfile'".format(self.dtype, self.name))
            else:
                self.dtype = "file"
                self.io = io
        else:
            self.dtype = TYPES[dtype]

        self.info = info
        self.default = default
        self.required = required
        self.choices = choices or []

        self.value = None


    def validate(self, value):
        if isinstance(self.dtype, list):
            if not isinstance(value, list) and not isinstance(value, self.dtype[1]):
                raise TypeError("Expecting type '{0}' for parameter '{1}', but got '{2}'".format(self.dtype[1], self.name, type(value)))
        elif not isinstance(value, tuple(TYPES.values())):
            raise TypeError("Expecting type '{0}' for parameter '{1}', but got '{2}'".format(self.dtype[1], self.name, type(value)))

        return True


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
        self.msdir = msdir

        if parameter_file:
            cab = utils.readJson(parameter_file)
            self.task = cab["task"]
            self.base = cab["base"]
            self.binary = cab["binary"]
            self.msdir = cab["msdir"]
            self.description = cab["description"]
            self.prefix = cab["prefix"]
            parameters0 = cab["parameters"]
            self.parameters = []

            for param in parameters0:
                try:
                    default = param["default"]
                except KeyError:
                    default = param["value"]

                addme = Parameter(name=param["name"],
                        dtype=param["dtype"],
                        io=param.get("io", None),
                        info=param.get("info", "No documentation. Bad! Very bad..."),
                        default=default,
                        required=param.get("required", False),
                        choices=param.get("choices", False))
                self.parameters.append(addme)

        else:
            self.task = task
            self.base = base
            self.binary = binary
            self.prefix = prefix
            self.parameters = parameters
            self.description = description

        
    def display(self):
        print("{}\n \n".format(self.description))
        print("Stimela Cab      {0}".format(self.task))
        print("Base Image       {0}".format(self.base))
        print("\n")

        print("Parameters:")
        for param in self.parameters:
            print("  Name         {}".format(param.name))
            print("  Description  {}".format(param.info))
            print("  Type         {}".format("file" if param.dtype=="file" else param.dtype.__name__))
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
            conf["parameters"].append(
                {
                    "name"      :   param.name,
                    "dtype"     :   "file" if param.dtype=="file" else param.dtype.__name__,
                    "info"      :   param.info,
                    "required"  :   param.required,
                    "value"     :   param.value or param.default,
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
                    if param.dtype=="file":
                        if not isinstance(value, str):
                            raise TypeError("Expecting type 'str' for parameter '{1}', but got '{2}'".format(self.name, type(value)))
                        val = value.split(":")
                        if len(val)==2:
                            self.log.info("Location of '{0}' was specified as '{1}'. Will overide default.".format(param.name, val[1]))
                            value = val[0]
                            location = val[1]
                        else:
                            location = param.io

                        if location in ["input", "msfile"] :
                            if location == "input" and self.indir is None:
                                raise IOError("You have specified input files, but have not specified an input folder")
                            if location == "msfile" and self.outdir is None:
                                raise IOError("You have specified MS files, but have not specified an MS folder")


                            path = "{0}/{1}".format(self.indir if location=="input" else self.msdir, value)
                            if not os.path.exists(path):
                                raise IOError("File '{0}' for parameter '{1}' could not be located at '{2}'.".format(value, param.name, location))
                            param.value = "{0}/{1}".format(IODEST[location], value)
                        else:
                            if self.outdir is None:
                                raise IOError("You have specified output files, but have not specified an output folder")
                            param.value = "{0}/{1}".format(IODEST[location], value)
                        
                    elif param.validate(value):
                        self.log.debug("Validating paramter {}".format(param.name))
                        param.value = value

        conf = {}
        conf.update(self.toDict())
        utils.writeJson(saveconf, conf)
        self.log.info("Parameters validated and saved. Parameter file is: {}".format(saveconf))
