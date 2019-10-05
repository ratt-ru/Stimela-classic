from stimela.RecipeStep import StepOutput
from scriptcwl import WorkflowGenerator
import os
import yaml
import ruamel.yaml


class RecipeCWL(object):
    def __init__(self, steps, collect=[], name=None, doc=None):
        """
            Convert StimelaSteps into a CWL workflow

            steps: StimelaSteps.Steps instance
        """
        self.steps = steps
        self.collect = collect
        self.inputs = {}
        self.name = name
        self.doc = doc

    def create_workflow(self):
        """
           Uses scriptcwl to convert a Stimela.Steps.Step into CWL workflow
        """
        wf = WorkflowGenerator()
        wf.set_documentation(self.doc)
        steps = {}
        for step in self.steps:
            # Add step cwlfile
            wf.load(step_file=step.cwlfile)
            stepname = os.path.basename(step.cwlfile)[:-4] # remove .cwl ext
            # Add step inputs and outputs
            inputs = {}
            for inparam in list(step.inputs.values()):
                # Check parameter depends on a preceding step
                if not isinstance(inparam.value, StepOutput):
                    # Add comment with input parameter name
                    inputs[inparam.param] = wf.add_input(**{inparam.name: inparam.dtype})
                    if inparam.dtype in ["File", "Directory"]:
                        self.inputs[inparam.name] = {
                            "class" : inparam.dtype,
                            "path"  : os.path.join(step.indir, inparam.value),
                        }
                    else:
                        self.inputs[inparam.name] = inparam.value

            # Start with steps that have no
            # workflow deps
            if not step.depends:
                steps[step.name] = getattr(wf, stepname)(**inputs)
            else:
                for key,value in list(step.depends.items()):
                    if isinstance(value, list):
                        _steps = []
                        vals = []
                        for item in value:
                            _step = steps[item.owner]
                            _steps.append(_step)
                            if isinstance(_step, list):
                                val = list(filter(lambda a: a.output_name==item.output, _step))[0]
                            else:
                                val = _step
                            vals.append(val)
                        val = vals
                    elif value.owner in steps:
                        _step = steps[value.owner]
                        # Find dependence if step has multiple outputs
                        if isinstance(_step, list):
                            val = list(filter(lambda a: a.output_name==value.output, _step))[0]
                        else:
                            val = _step
                    inputs[key] = val
                steps[step.name] = getattr(wf, stepname)(**inputs)
        
        wf.validate()
        self.workflow = wf
        # Add workfkow output products
        for item in self.collect:
            if isinstance(steps[item], (list,tuple)):
                for i,item_i in enumerate(steps[item]):
                    wf.add_outputs(**{"{0:s}_{1:d}".format(item, i): item_i})
                continue
            wf.add_outputs(**{"{0:s}".format(item): steps[item]})
        return 0

    def write(self, name=None):
        """
           Save workflow and job file
        """
        name = self.name or name
        self.workflow_file = name + ".cwl"
        self.job_file = name + '.yml'
        self.workflow.save(self.workflow_file, mode="abs")
        repeated_stepnames = {}
        # Check if any steps has InplaceUpdate requirement
        for step in self.steps:
            stepfile = getattr(step, "original_cwlfile", None)
            stepname = os.path.basename(step.cwlfile)[:-4]
            if stepname in repeated_stepnames:
                repeated_stepnames[stepname] += 1
            else:
                repeated_stepnames[stepname] = 0

            if stepfile:
                if repeated_stepnames[stepname] > 0:
                    stepname_ = "{0:s}-{1:d}".format(stepname, 
                            repeated_stepnames[stepname])
                else:
                    stepname_ = stepname
                with open(self.workflow_file, "r") as stdr:
                    workflow = ruamel.yaml.load(stdr, ruamel.yaml.RoundTripLoader)
                    # Replace with cwlfile that has InplaceUpdate requirement
                    workflow["steps"][stepname_]["run"] = stepfile
                with open(self.workflow_file, "w") as stdw:
                    ruamel.yaml.dump(workflow, stdw, Dumper=ruamel.yaml.RoundTripDumper)
                # Remember to delete temporary file
                if os.path.exists(step.cwlfile):
                    os.remove(step.cwlfile)
        if self.inputs:
            with open(self.job_file, 'w') as stdw:
                yaml.dump(self.inputs, stdw, default_flow_style=False)

        return 0
