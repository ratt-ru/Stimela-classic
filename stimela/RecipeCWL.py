from RecipeStep import StepOutput
from scriptcwl import WorkflowGenerator
import os
import yaml


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
            for inparam in step.inputs.values():
                # Check parameter depends on a preceding step
                if not isinstance(inparam.value, StepOutput):
                    # Add comment with input parameter name
                    # Use hash to avoid clash when different steps have same input name
                    inputs[inparam.param] = wf.add_input(**{inparam.hash: inparam.dtype})
                    if inparam.dtype in ["File", "Directory"]:
                        self.inputs[inparam.hash] = {
                            "class" : inparam.dtype,
                            "path"  : inparam.value
                        }
                    else:
                        self.inputs[inparam.hash] = inparam.value

            # Start with steps that have no
            # workflow deps
            if not step.depends:
                steps[step.name] = getattr(wf, stepname)(**inputs)
            else:
                for key,value in step.depends.iteritems():
                    if value.owner in steps:
                        _step = steps[value.owner]
                        # Find dependence if step has multiple outputs
                        if isinstance(_step, list):
                            val = filter(lambda a: a.output_name==value.output, _step)[0]
                        else:
                            val = _step
                        inputs[key] = val
                steps[step.name] = getattr(wf, stepname)(**inputs)
        
        wf.validate()
        self.workflow = wf
        # Add workfkow output products
        for item in self.collect:
            wf.add_outputs(**{"{0:s}_outputs".format(item): steps[item]})

        return 0

    def write(self, name=None):
        """
           Save workflow and job file
        """
        name = self.name or name
        self.workflow_file = name + ".cwl"
        self.job_file = name + '.yml'
        self.workflow.save(self.workflow_file)
        if self.inputs:
            with open(self.job_file, 'w') as stdw:
                yaml.dump(self.inputs, stdw, default_flow_style=False)

        return 0
