import os
import sys
import inspect
import logging
import re
import time
from stimela.RecipeStep import Step
import logging
from stimela.RecipeCWL import Workflow
import subprocess
import warnings

CWLDIR = os.path.join(os.path.dirname(__file__), "cargo/cab")

class Recipe(object):
    """
      Functions for defining and executing a stimela recipe
    """
    def __init__(self, name, indir, outdir,
                 msdir=None,
                 cachedir=None,
                 loglevel="INFO",
                 loggername="STIMELA",
                 logfile=None,
                 toil=False):

        """
        Parameters
        ----------

        name: str
            Name of recipe.
        indir: str
            Path to directory where recipe inputs are stored
        outdir: str
            Path to directory where recipe outputs should be saved
        msdir: str|bool
            Path to directory where MS files are saved, or should be saved. If an MS will be created
        cachedir: str
            Cache directory
        loglevel: str
            Log level INFO|DEBUG|ERROR
        loggername: str
            Name of logger instance. This is useful when running multiple instances of stimela
        logfile: str
            Name of file to dump recipe logging information
        toil: bool
            Use toil runner instead of CWL reference runner
        """
        self.name = name
        self.name_ = name.lower().replace(' ', '_')
        self.indir = indir
        self.outdir = outdir
        self.cachedir = cachedir
        # Create outdir if it does not exist
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        self.msdir = msdir
        self.loglevel = loglevel
        self.logfile = logfile or "log-{0:s}.txt".format(self.name_)
        self.log = logging.getLogger(loggername)
        self.log.setLevel(getattr(logging, self.loglevel))
        fh = logging.FileHandler(self.logfile, 'w')
        fh.setLevel(logging.DEBUG)
        # Create console handler with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(getattr(logging, self.loglevel))
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # Add the handlers to logger
        self.log.addHandler(ch)
        self.log.addHandler(fh)
        self.TBC = "dummy_variable_that_no_one_will_ever_use_surely"

        self.steps = []
        self.toil = toil


    def add(self, task, label, parameters=None, doc=None, cwlfile=None, workflow=False, scatter=[]):
        """ Add task to recipe
        
        Parameters
        ----------

        task: str
            Name of task to run. For a stimela task, use the name of the cwlfile (without the .cwl extension)
            If running a task that uses a custom cwlfile, then name of the task does not have 
            to match the name of the cwlfile
        label: str
            Label for task. Must be alphanumereic
        parameters: dict
            Dictionary of input parameters and their values
        doc: str
            Task documentation. 
        cwlfile: str
            Path to cwlfile if not using a stimela cwlfile
        """
        if workflow:
            if not hasattr(task, 'workflow'):
                warnings.warn("Recipe %s is not registered. Will register"
                              " it before proceeding" % task.name)
                task.init()
            cwlfile = task.workflow.workflow_file

            # first update workflow parameters with workflow inputs
            for param in parameters:
                task.inputs[param] = parameters[param]
            parameters = task.inputs
            for param in parameters:
                if isinstance(parameters[param], dict):
                    parameters[param] = parameters[param]["path"]
        else:
            if parameters is None:
                self.log.abort("No parameters were parsed into the %s. Please review your recipe." % label)
            cwlfile = cwlfile or "{0:s}/{1:s}.cwl".format(CWLDIR, task)
            self.log.info("Adding step [{:s}] to recipe".format(task))

        step = Step(label, parameters, cwlfile, indir=self.indir, scatter=scatter)

        # add step as recipe attribute
        setattr(self, label, step)

        self.steps.append(step)

    def collect_outputs(self, outputs):
        """ Recipe outputs to save after execution. All other products will be deleted

        Parameters
        ---------

        outputs: list
            List of recipe outputs to collect (save/keep). For example, 
            if you want the collect the of step with 'step = Recipe.add(task, label)'
            you should use Recipe.collect_outputs(["label"]). If step has multiple outputs, 
            the use Recipe.collect_outputs(["label/out1", "label/out2", ...])

        """
        self.collect = outputs

    def init(self):
        """
        Initialise pipeline. This is useful if you plan on combining multiple workflows
        """
        self.workflow = Workflow(self.steps, collect=self.collect,
                                  name=self.name_, doc=self.name)

        self.workflow.create_workflow()
        self.workflow.write()
        self.inputs = self.workflow.inputs

    def run(self):
        """
        Run Recipe
        """
        if not hasattr(self, "workflow"):
            self.init()

        if self.toil:
            subprocess.check_call([
                "cwltoil",
                "--enable-ext",
                "--logFile", self.logfile,
                "--outdir", self.outdir,
                self.workflow.workflow_file,
                self.workflow.job_file,
            ])
        else:
            if self.cachedir:
                cache = ["--cachedir", self.cachedir]
            else:
                cache = []
            subprocess.check_call([
                "cwltool",
                "--enable-ext",
                "--outdir", self.outdir,
            ] + cache + [
                self.workflow.workflow_file,
                self.workflow.job_file,
            ])

        return 0
