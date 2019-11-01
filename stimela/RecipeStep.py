import os
import sys
import cwltool.factory
import ruamel.yaml
import tempfile
import collections

class StepParameter(object):
    def __init__(self, value, owner, dtype, param, scatter=False):
        self.value = value
        self.owner = owner
        #TODO: Need a better way to do this. It will certainly be a pain
        self.dtype = dtype[-1] if isinstance(dtype, list) else dtype
        self.param = param
        # Create a hash (step name+param) for the case where different steps can have same input parameter name
        self.name = "_".join([self.owner, self.param])
        inthash = hash(frozenset(list({self.owner: param}.items())))
        self.hash = "h{}".format(abs(inthash))
        self.scatter = scatter
        if isinstance(value, list) and self.scatter and self.dtype.find("[]")<0:
            print(self.param)
            self.dtype = collections.OrderedDict([('type', 'array'), ('items', self.dtype)])

class StepOutput(object):
    def __init__(self, owner, output):
        self.owner = owner
        self.output = output

class Step(object):
    def __init__(self, name, params, cwlfile, indir=None, scatter=[]):
        """ 
            Recipe step class

            name: Step name
            params: input parameters
        """
        self.name = name
        self.params = params
        self.indir = indir
        self.cwlfile = cwlfile
        self.optional_outputs = []
        self.scatter = scatter

        ## Get version of file that does not have extensions so we can load it. This will also help when making the workflow with scriptcwl
        with open(self.cwlfile, "r") as stdr:
            step_def = ruamel.yaml.load(stdr, ruamel.yaml.RoundTripLoader)
        self.__namespaces = step_def.get("$namespaces", None)
        if self.__namespaces:
            del step_def["$namespaces"]
            self.__requirements = step_def.get("requirements")
            requirements = []
            for ns in self.__namespaces:
                for req in self.__requirements:
                    if not req["class"].startswith(ns):
                        requirements.append(req)
            # Set requirements and exclude the namespace classes
            step_def["requirements"] = requirements

            self.original_cwlfile = self.cwlfile
            self.cwlfile = "/".join(["/tmp", os.path.basename(self.original_cwlfile)])
            with open(self.cwlfile, mode="w+t") as stdwt:
                ruamel.yaml.dump(step_def, stdwt, Dumper=ruamel.yaml.RoundTripDumper)

        self.tool = cwltool.factory.Factory().make(self.cwlfile)
        self.outputs = self.__set_outputs()
        self.inputs, self.depends = self.__set_params()

    def __any_deps(self, value):
        for val in value:
            if isinstance(val, StepOutput):
                return True
        return False

    def __set_params(self):
        """
            Set step parameters
        """
        fields = self.tool.t.inputs_record_schema["fields"]
        names = [ field["name"] for field in fields ]
        inputs = {}
        depends = {}
        for key,value in list(self.params.items()):
            index = names.index(key)
            if isinstance(value, StepOutput):
                depends[key] = value
            elif isinstance(value, list) and self.__any_deps(value):
                depends[key] = []
                values = []
                for val in value:
                    if isinstance(val, StepOutput):
                        depends[key].append(val)
                    else:
                        values.append(val)
                if values:
                    parameter = StepParameter(values, self.name, fields[index]["type"],
                            key, scatter=key in self.scatter)
            else:
                parameter = StepParameter(value, self.name, fields[index]["type"], 
                        key, scatter=key in self.scatter)
                inputs[key] = parameter

        return inputs, depends

    def __set_outputs(self):
        """
            Set step parameters
        """
        fields = self.tool.t.outputs_record_schema["fields"]
        outputs = {}
        for field in fields:
            outputs[field["name"]] = StepOutput(self.name, field["name"])
            dtype = field["type"]
            if isinstance(dtype, list):
                if dtype[0] == "null":
                    self.optional_outputs.append(field["name"])

        return outputs
