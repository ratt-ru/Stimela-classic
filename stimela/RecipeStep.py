import os
import cwltool.factory

class StepParameter(object):
    def __init__(self, value, owner, dtype, param):
        self.value = value
        self.owner = owner
        #TODO: Need a better way to do this. It will certainly be a pain
        self.dtype = dtype[-1] if isinstance(dtype, list) else dtype
        self.param = param
        # Create a hash (step name+param) for the case where different steps can have same input parameter name
        inthash = hash(frozenset({self.owner: param}.items()))
        self.hash = "h{}".format(abs(inthash))


class StepOutput(object):
    def __init__(self, owner, output):
        self.owner = owner
        self.output = output


class Step(object):
    def __init__(self, name, params, cwlfile, indir=None):
        """ 
            Recipe step class

            name: Step name
            params: input parameters
        """

        self.name = name
        self.params = params
        self.indir = indir
        self.cwlfile = cwlfile
        self.tool = cwltool.factory.Factory().make(self.cwlfile)
        self.outputs = self.__set_outputs()
        self.inputs, self.depends = self.__set_params()

    def __set_params(self):
        """
            Set step parameters
        """

        fields = self.tool.t.inputs_record_schema["fields"]
        names = [ field["name"] for field in fields]
        inputs = {}
        depends = {}
        for key,value in self.params.iteritems():
            index = names.index(key)
            if isinstance(value, StepOutput):
                depends[key] = value
            else:
                parameter = StepParameter(value, self.name, fields[index]["type"], key)
                if parameter.dtype in ["File", "Directory"]:
                    parameter.value = os.path.join(self.indir, value)
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

        return outputs
