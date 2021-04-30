import glob
import os, os.path, re, logging
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass
from omegaconf import MISSING, OmegaConf, DictConfig
from collections import OrderedDict
from stimela.config import EmptyDictDefault
import stimela
from stimela import logger

from stimela.exceptions import *

from scabha import validate
from scabha.validate import join_quote

from . import runners


Conditional = Optional[str]

from scabha.cargo import Cargo, Cab

@dataclass
class Step:
    """Represents one processing step of a recipe"""
    cab: Optional[str] = None                       # if not None, this step is a cab and this is the cab name
    recipe: Optional["Recipe"] = None               # if not None, this step is a nested recipe
    params: Dict[str, Any] = EmptyDictDefault()     # assigns parameter values
    info: Optional[str] = None                      # comment or info

    _skip: Conditional = None                       # skip this step if conditional evaluates to true
    _break_on: Conditional = None                   # break out (of parent receipe) if conditional evaluates to true

    def __post_init__(self):
        if bool(self.cab) == bool(self.recipe):
            raise StepValidationError("step must specify either a cab or a nested recipe, but not both")
        self.cargo = self.config = self.log = None
        self._prevalidated = None
        # convert params into stadard dict, else lousy stuff happens when we imnsetr non-standard objects
        if isinstance(self.params, DictConfig):
            self.params = OmegaConf.to_container(self.params)

    @property
    def summary(self):
        return self.cargo and self.cargo.summary 

    @property
    def finalized(self):
        return self.cargo is not None

    @property
    def prevalidated(self):
        return self._prevalidated

    @property
    def missing_params(self):
        return self.cargo.missing_params

    @property
    def invalid_params(self):
        return self.cargo.invalid_params

    @property
    def unresolved_params(self):
        return self.cargo.unresolved_params

    @property
    def inputs(self):
        return self.cargo.inputs

    @property
    def outputs(self):
        return self.cargo.outputs

    @property
    def inputs_outputs(self):
        return self.cargo.inputs_outputs

    def update_parameter(self, name, value):
        self.params[name] = value
        # only pass value up to cargo if has already been validated. This avoids redefinition errors from nested aliases.
        # otherwise, just keep the value in our dict (cargo will get it upon validation)
        if self.cargo is not None and self.prevalidated:
            self.cargo.update_parameter(name, value)

    def finalize(self, config=None, log=None, full_name=None):
        if not self.finalized:
            self.log = log or stimela.logger()
            self.config = config or stimela.CONFIG
            if bool(self.cab) == bool(self.recipe):
                raise StepValidationError("step must specify either a cab or a nested recipe, but not both")
            # if recipe, validate the recipe with our parameters
            if self.recipe:
                # instantiate from omegaconf object, if needed
                if type(self.recipe) is not Recipe:
                    self.recipe = Recipe(**self.recipe)
                self.cargo = self.recipe
            else:
                if self.cab not in self.config.cabs:
                    raise StepValidationError(f"unknown cab {self.cab}")
                self.cargo = Cab(**config.cabs[self.cab])
            # note that cargo is passed log (which could be None), so it can sort out its own logger
            self.cargo.finalize(config, log=log, full_name=full_name)

    def prevalidate(self):
        if not self.prevalidated:
            self.finalize()
            # validate cab or recipe
            self.cargo.prevalidate(self.params)
            self.log.debug(f"{self.cargo.name}: {len(self.missing_params)} missing, "
                            f"{len(self.invalid_params)} invalid and "
                            f"{len(self.unresolved_params)} unresolved parameters")
            if self.invalid_params:
                raise StepValidationError(f"{self.cargo.name} has the following invalid parameters: {join_quote(self.invalid_params)}")

    def run(self, subst=None):
        """Runs the step"""
        self.prevalidate()
        subst = subst or OmegaConf.create({'config': self.config})

        self.log.info(f"validating inputs")
        try:
            params = self.cargo.validate_inputs(self.params, subst)
        except ScabhaBaseException as exc:
            if not exc.logged:
                self.log.error(f"error validating inputs: {exc}")
            raise

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("---------- validated inputs ----------")
            for line in self.summary:
                self.log.debug(line)

        # bomb out if some inputs failed to validate or substitutions resolve
        if self.cargo.invalid_params or self.cargo.unresolved_params:
            invalid = self.cargo.invalid_params + self.cargo.unresolved_params
            raise StepValidationError(f"invalid inputs: {join_quote(invalid)}", log=self.log)

        self.log.info(f"running step")
        try:
            if type(self.cargo) is Recipe:
                self.cargo._run(subst)
            elif type(self.cargo) is Cab:
                runners.run_cab(self.cargo, log=self.log)
            else:
                raise RuntimeError("Unknown cargo type")
        except ScabhaBaseException as exc:
            if not exc.logged:
                self.log.error(f"error running step: {exc}")
            raise

        self.log.info(f"validating outputs")
        # insert output values into params for re-substitution and re-validation
        try:
            params = self.cargo.validate_outputs(params, subst)
        except ScabhaBaseException as exc:
            if not exc.logged:
                self.log.error(f"error validating outputs: {exc}")
            raise

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("---------- validated outputs ----------")
            for line in self.summary:
                self.log.debug(line)

        # again, bomb put if something was invalid
        if self.cargo.invalid_params or self.cargo.unresolved_params:
            invalid = self.cargo.invalid_params + self.cargo.unresolved_params
            raise StepValidationError(f"invalid inputs: {join_quote(invalid)}", log=self.log)


        return {name: value for name, value in params.items() if name in self.outputs}

@dataclass
class ForLoopClause(object):
    # name of list variable
    var: str 
    # This should be the name of an input that provides a list.
    over: str
    # If True, this is a for_loop not a loop -- things may be evaluated in parallel
    for_loop: bool = False



@dataclass
class Recipe(Cargo):
    """Represents a sequence of steps.

    Additional attributes available after validation with arguments are as per for a Cab:

        self.input_output:      combined parameter dict (self.input + self.output), maps name to Parameter
        self.missing_params:    dict (name to Parameter) of required parameters that have not been specified

    Raises:
        various classes of validation errors
    """
    steps: Dict[str, Step] = EmptyDictDefault()     # sequence of named steps

    dirs: Dict[str, Any] = EmptyDictDefault()       # I/O directory mappings

    vars: Dict[str, Any] = EmptyDictDefault()       # arbitrary collection of variables pertaining to this step (for use in substitutions)

    aliases: Dict[str, Any] = EmptyDictDefault()

    defaults: Dict[str, Any] = EmptyDictDefault()

    # make recipe a for_loop-gather (i.e. parallel for loop)
    for_loop: Optional[ForLoopClause] = None

    # logging control
    logfile: Optional[str] = "log-{name}.txt"       # recipe logfile. None uses default logger. {name} is substituted
    loglevel: str = "INFO"                          # level at which we log
    nest_logs: bool = True                          # if True, each step gets an individual logfile. 
    

    # if not None, do a while loop with the conditional
    _while: Conditional = None
    # if not None, do an until loop with the conditional
    _until: Conditional = None

    def __post_init__ (self):
        Cargo.__post_init__(self)
        for name, alias_list in self.aliases.items():
            if name in self.inputs_outputs:
                raise RecipeValidationError(f"alias '{name}'' also appears under inputs or outputs")
            if type(alias_list) is str:
                alias_list = self.aliases[name] = [alias_list]
            if not hasattr(alias_list, '__iter__') or not all(type(x) is str for x in alias_list):
                raise RecipeValidationError(f"alias '{name}': name or list of names expected")
            for x in alias_list:
                if '.' not in x:
                    raise RecipeValidationError(f"alias '{name}': invalid target '{x}' (missing dot)")
        # instantiate steps if needed (when creating from an omegaconf)
        if type(self.steps) is not OrderedDict:
            steps = OrderedDict()
            for label, stepconfig in self.steps.items():
                steps[label] = Step(**stepconfig)
            self.steps = steps
        # map of aliases
        self._alias_map = None
        self.log = logger()

 
    @property
    def finalized(self):
        return self._alias_map is not None


    def add_step(self, step: Step, label: str = None):
        """Adds a step to the recipe. Label is auto-generated if not supplied

        Args:
            step (Step): step object to add
            label (str, optional): step label, auto-generated if None
        """
        if self.finalized:
            raise DefinitionError("can't add a step to a recipe that's been finalized")

        names = [s for s in self.steps if s.cab == step.cabname]

        self.steps[label or f"{step.cabname}_{len(names)+1}"] = step


    def add(self, cabname: str, label: str = None, 
            params: Optional[Dict[str, Any]] = None, info: str = None):
        """Add a step to a recipe. This will create a Step instance and call add_step() 

        Args:
            cabname (str): name of cab to use for this step
            label (str): Alphanumeric label (must start with a lette) for the step. If not given will be auto generated 'cabname_d' where d is the number of times a particular cab has been added to the recipe.
            params (Dict): A parameter dictionary
            info (str): Documentation of this step
        """
        return self.add_step(Step(cab=cabname, params=params, info=info), label=label)


    def _add_alias(self, alias_name, step_label, step, step_param_name):
        is_input = schema = step.inputs.get(step_param_name)
        if schema is None:
            schema = step.outputs.get(step_param_name)
            if schema is None:
                raise RecipeValidationError(f"alias '{alias_name}' refers to unknown parameter '{step_label}.{step_param_name}'")
        # check that it's not already set
        if step_param_name in step.params:
            raise RecipeValidationError(f"alias '{alias_name}' refers parameter '{step_label}.{step_param_name}' that is already set")
        # add to our mapping
        io = self.inputs if is_input else self.outputs
        existing_schema = io.get(alias_name)
        if existing_schema is None:                   
            io[alias_name] = schema.copy()
        else:
            # check if definition conflicts
            if bool(is_input) != bool(io is self.inputs) or schema.dtype != existing_schema.dtype:
                raise RecipeValidationError(f"alias '{alias_name}' has a conflicting list of definitions (dtype of '{step_label}.{step_param_name}' doesn't match previous dtype)")
            # alias becomes required if any parm it refers to was required, unless recipe has a default
            if schema.required:
                existing_schema.required = True
        
        self._alias_map[step_label, step_param_name] = alias_name
        self._alias_list.setdefault(alias_name, []).append((step, step_param_name))


    def _make_file_logger(self, name):
        log = logger().getChild(name)
        log.propagate = True # propagate to main stimela logger

        # finalize logfile name
        name = re.sub(r'[^a-zA-Z0-9_.-]', '_', name)
        logfile = self.logfile.format(name=name)

        if "log" in self.dirs:
            if "/" not in logfile:
                logfile = os.path.join(self.dirs.log, logfile)

        # ensure directory exists
        log_dir = os.path.dirname(logfile) or "."
        if not os.path.exists(log_dir):
            log.info(f'creating log directory {log_dir}')
            os.makedirs(log_dir)

        log_fh = logging.FileHandler(logfile, 'w', delay=True)
        log_fh.setLevel(getattr(logging, self.loglevel))
        log_fh.setFormatter(stimela.log_formatter)
        log.addHandler(log_fh)
        return log


    def finalize(self, config=None, log=None, full_name=None):
        if not self.finalized:
            config = config or stimela.CONFIG
            log = log or stimela.logger()
            full_name = full_name or self.name
            # setup recipe-level logging
            if log is None:
                if not self.logfile:
                    log = logger()
                else:
                    log = self._make_file_logger(full_name)

            Cargo.finalize(self, config, log=log, full_name=full_name)

            # finalize step cargos
            for label, step in self.steps.items():
                step_full_name = f"{full_name}.{label}"
                if self.nest_logs:
                    log = self._make_file_logger(step_full_name)
                step.finalize(config, full_name=step_full_name, log=log)

            # collect aliases
            self._alias_map = OrderedDict()
            self._alias_list = OrderedDict()

            for name, alias_list in self.aliases.items():
                for alias in alias_list:
                    # verify mapped name
                    step_label, step_param_name = alias.split('.', 1)
                    step = self.steps.get(step_label)
                    if step is None:
                        raise RecipeValidationError(f"alias {name} refers to unknown step '{step_label}'", log=log)
                    self._add_alias(name, step_label, step, step_param_name)

            # automatically make aliases for unset required parameters 
            for label, step in self.steps.items():
                for name, schema in step.inputs_outputs.items():
                    if (label, name) not in self._alias_map and name not in step.params and schema.required:
                        auto_name = f"{label}_{name}"
                        if auto_name in self.inputs or auto_name in self.outputs:
                            raise RecipeValidationError(f"auto-generated parameter name '{auto_name}' conflicts with another name. Please define an explicit alias for this.", log=log)
                        self._add_alias(auto_name, label, step, name)

            # these will be re-merged when needed again
            self._inputs_outputs = None

            # check that for-loop is valid, if defined
            if self.for_loop is not None:
                if self.for_loop.over not in self.inputs:
                    raise RecipeValidationError(f"for_loop list '{self.for_loop.over}' is not a defined input", log=log)
                # this becomes a required input
                self.inputs[self.for_loop.over].required = True
                # mark loop variable as unresolved
                self.update_parameter(self.for_loop.var, validate.Unresolved(self.for_loop.var))


    def prevalidate(self, params: Optional[Dict[str, Any]]):
        self.finalize()
        self.log.info("prevalidating recipe")
        errors = []

        # check params
        if self.for_loop and self.for_loop.var in self.params and type(self.params[self.for_loop.var]) is not validate.Unresolved:
            errors.append(RecipeValidationError(f"value of for_loop variable '{self.for_loop.var}' cannot be set explicitly", log=self.log))

        # validate our own parameters without substitutions
        try:
            Cargo.prevalidate(self, params)
        except ScabhaBaseException as exc:
            msg = f"recipe pre-validation failed: {exc}"
            errors.append(RecipeValidationError(msg, log=self.log))

        # propagate aliases up to substeps
        for name, value in self.params.items():
            self._propagate_parameter(name, value)
        # mark loop variable as an unresolved substitution for now
        if self.for_loop is not None:
            self.update_parameter(self.for_loop.var, validate.Unresolved(self.for_loop.var))

        # check for missing ones
        if self.missing_params:
            msg = f"""recipe '{self.name}' is missing the following required parameters: {join_quote(self.missing_params)}"""
            errors.append(RecipeValidationError(msg, log=self.log))

        # prevalidate step parameters 
        for label, step in self.steps.items():
            try:
                step.prevalidate()
            except ScabhaBaseException as exc:
                msg = f"step '{label}' failed pre-validation: {exc}"
                errors.append(RecipeValidationError(msg, log=self.log))

        if errors:
            raise RecipeValidationError(f"{len(errors)} error(s) validating the recipe '{self.name}'", log=self.log)

        self.log.info("recipe pre-validated")
        return

    def validate_inputs(self, params: Dict[str, Any], subst: Optional[Dict[str, Any]]):
        # for loops, and an unresolved loop variable to the parameters so that it validates
        if self.for_loop is not None:
            self._for_loop_values = self.params[self.for_loop.over]
            if not isinstance(self._for_loop_values, (list, tuple)):
                self._for_loop_values = [iter_values]
            self.log.info(f"recipe is a for-loop with '{self.for_loop.var}' iterating over {len(self._for_loop_values)} values")
            params = params.copy()
            params[self.for_loop.var] = self._for_loop_values[0]
        else:
            self._for_loop_values = [None]
        return Cargo.validate_inputs(self, params, subst)


    def _propagate_parameter(self, name, value):
        ### OMS: not sure why I had this, why not propagae unresolveds?
        ## if type(value) is not validate.Unresolved:
        for step, step_param_name in self._alias_list.get(name, []):
            if self.inputs_outputs[name].implicit:
                if step_param_name in step.cargo.params:
                    self.params[name] = step.cargo.params[name]
            else:
                step.update_parameter(step_param_name, value)

    def update_parameter(self, name: str, value: Any):
        """[summary]

        Parameters
        ----------
        name : str
            [description]
        value : Any
            [description]
        """
        self.params[name] = value
        # resolved values propagate up to substeps if aliases, and propagate back if implicit
        self._propagate_parameter(name, value)

    @property
    def summary(self):
        """Returns list of lines with a summary of the recipe state
        """
        lines = [f"recipe '{self.name}':"] + [f"  {name} = {value}" for name, value in self.params.items()] + \
                [f"  {name} = ???" for name in self.missing_params]
        lines.append("  steps:")
        for name, step in self.steps.items():
            stepsum = step.summary
            lines.append(f"    {name}: {stepsum[0]}")
            lines += [f"    {x}" for x in stepsum[1:]]
        return lines


    def _run(self, subst: Optional[DictConfig]=None) -> Dict[str, Any]:
        """Internal recipe run method. Meant to be called from a wrapper Step object (which validates the parameters, etc.)

        Parameters
        ----------
        subst : DictConfig, optional
            OmegaConf dictionary of substitutions applied to parameters

        Returns
        -------
        Dict[str, Any]
            Dictionary of formal outputs

        Raises
        ------
        RecipeValidationError
        """
        self.log.info(f"running recipe '{self.name}'")

        if subst is None:
            subst = OmegaConf.create()

        # our inputs have been validated, so propagate aliases to steps. Check for missing stuff just in case
        for name, schema in self.inputs.items():
            if name in self.params:
                value = self.params[name]
                if type(value) is validate.Unresolved:
                    raise RecipeValidationError(f"recipe '{self.name}' has unresolved input '{name}'", log=self.log)
                # propagate up all aliases
                for step, step_param_name in self._alias_list.get(name, []):
                    step.update_parameter(step_param_name, value)
            else:
                if schema.required: 
                    raise RecipeValidationError(f"recipe '{self.name}' is missing required input '{name}'", log=self.log)

        # set up substitutions and run the steps
        subst1 = subst.copy() if subst else OmegaConf.create({'config': self.config})
        subst1.recipe = self.make_substitition_namespace()
        subst1.steps  = OmegaConf.create()
        subst1.previous = None

        # iterate over for-loop values (if not looping, this is set up to [None] in advance)
        for count, iter_var in enumerate(self._for_loop_values):
            if self.for_loop:
                self.log.info(f"for loop iteration {count}: {self.for_loop.var} = {iter_var}")
                self.update_parameter(self.for_loop.var, iter_var)
                subst1.recipe[self.for_loop.var] = iter_var

            for label, step in self.steps.items():
                try:
                    step_outputs = step.run(subst1)
                except StimelaBaseException as exc:
                    if not exc.logged:
                        self.log.error(f"error running step '{label}': {exc}")
                    raise
                # put all step parameters into the substitution dict, as they're all validated now
                subst1.previous = OmegaConf.create(step.cargo.params)
                subst1.steps[label] = subst1.previous

                # check aliases, our outputs need to be retrieved from the step
                for name, schema in self.outputs.items():
                    for step1, step_param_name in self._alias_list.get(name, []):
                        if step1 is step and step_param_name in step_outputs:
                            self.params[name] = step_outputs[step_param_name]
                            # clear implicit setting
                            self.outputs[name].implicit = None

        self.log.info(f"recipe '{self.name}' executed successfully")
        return {name: value for name, value in self.params.items() if name in self.outputs}


    def run(self, **params) -> Dict[str, Any]:
        """Public interface for running a step. Keywords are passed in as step parameters

        Returns
        -------
        Dict[str, Any]
            Dictionary of formal outputs
        """
        return Step(recipe=self, params=params, info=f"wrapper step for recipe '{self.name}'").run()