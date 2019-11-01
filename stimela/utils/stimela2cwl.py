import ruamel.yaml as yaml
import os
import sys
import logging as log
import collections
import os
import sys

infile = sys.argv[1]

with open(infile, "r") as stdr:
    log.info("Loading stimela parameter file")
    stimela_params = yaml.load(stdr, yaml.RoundTripLoader)

taskname = stimela_params["task"]

base = stimela_params["base"]
tag = stimela_params["tag"]

## Auto generated cwl file
cwl_params_string = """
cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: {0:s}:{1:s}
  InlineJavascriptRequirement: {{}}
""".format(base, tag)

casa = taskname.startswith("casa_")

if casa:
    cwl_params_string += """\n
arguments:
  - prefix: -c  
    valueFrom: |
      from __future__ import print_function
      import Crasa.Crasa as crasa
      import sys 

      # JavaScript uses lowercase for bools
      true = True
      false = False
      null = None

      args = ${
        var values = {}; 

        for (var key in inputs) {
            var value = inputs[key];
            if (value) {
              if (value.class == 'Directory') {
                values[key] = value.path;
              } else {
                values[key] = value;
              }
            }
        }
        return values;
      }
      print(args, file=sys.stderr)
      task = crasa.CasaTask("%s", **args)
      task.run()
""" % taskname.split("_")[-1]

cwl_params = yaml.load(cwl_params_string, yaml.RoundTripLoader)
cwl_params["baseCommand"] = stimela_params["binary"]
cwl_params["inputs"] = {} 
cwl_params["outputs"] = {}

if stimela_params["msdir"]:
   ms = [a for a in stimela_params["parameters"] if a["name"] in "msname ms vis visfile msfile".split()]
   if ms:
        ms = list(ms)[0]
        name = ms.get("mapping", None) or ms.get("name")
        cwl_params["requirements"]["InitialWorkDirRequirement"] = { "listing" : [
                { "entry" : "$(inputs.{0:s})".format(name),
                           "writable" : True, 
            }]
        }
        
TYPES = {
    "str"       : "string",
    "int"       : "int",
    "float"     : "float",
    "bool"      : "boolean",
    "file"      : "File",
}

prefix = stimela_params["prefix"]
outputs = []
for param in stimela_params["parameters"]:
    default = param.get("default", None)
    _dtype = param.get("dtype")
    doc = param.get("info", "No documentation")
    if isinstance(_dtype, str):
        _dtype = [_dtype]
    repeat = len(_dtype) > 1
    # check if parameter accepts multiple types
    for _type in _dtype:
        name = param.get("mapping", None) or param.get("name")
        symbols = param.get("choices", None)

        if _type.startswith("list:"):
            islist = True
        else: 
            islist = False
        _type = _type.split(":")[-1]

        if param.get("io", False):
            if param["io"] == "msfile":
                dtype = "Directory"
            elif param["io"] == "output":
                outputs.append(param)
                continue
            elif param["io"] == "input":
                dtype = "File"
        elif repeat:
            dtype = "str"
        else:
            dtype = _type

        if islist:
            dtype =  TYPES[_type] + "[]"
        else:
            dtype =  TYPES[_type]

        if not param.get("required", False):
            dtype += "?"

        # append type if param accepts multiple types
        cwl_params["inputs"][name] = {
            "type" : dtype,
            "doc"  : doc,
        }

        if symbols:
            cwl_params["inputs"][name]["type"] = {"type" : "enum", "symbols": symbols}
        if not casa:
            cwl_params["inputs"][name]["inputBinding"] = {
                    "prefix" : "{0:s}{1:s}".format(prefix, name),
                    }

cwl_params["outputs"] = outputs

with open(taskname+".cwl", "w") as stdw:
    yaml.dump(cwl_params, stdw, Dumper=yaml.RoundTripDumper, indent=2, block_seq_indent=2)
