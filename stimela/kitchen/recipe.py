import glob
import os, os.path
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from omegaconf import omegaconf
from omegaconf.omegaconf import MISSING, OmegaConf
from collections import OrderedDict
from stimela.config import EmptyDictDefault, EmptyListDefault, Parameter, CabManagement
from stimela import logger

from stimela.exceptions import *

from stimela.kitchen import validate
from stimela.kitchen.validate import validate_parameters


Conditional = Optional[str]



@dataclass
class Cargo(object):
    name: Optional[str] = None                    # cab name. (If None, use image or command name)
    info: Optional[str] = None                    # description
    inputs: Dict[str, Parameter] = EmptyDictDefault()
    outputs: Dict[str, Parameter] = EmptyDictDefault()
    defaults: Dict[str, Any] = EmptyDictDefault()

    def __post_init__(self):
        for name in self.inputs.keys():
            if name in self.outputs:
                raise DefinitionError(f"{name} appears in both inputs and outputs")
        self.params = {}
        self._inputs_outputs = None

    @property
    def inputs_outputs(self):
        if self._inputs_outputs is None:
            self._inputs_outputs = self.inputs.copy()
            self._inputs_outputs.update(**self.outputs)
        return self._inputs_outputs
    
    @property
    def invalid_params(self):
        return [name for name, value in self.params.items() if type(value) is validate.Error]

    @property
    def missing_params(self):
        return {name: schema for name, schema in self.inputs_outputs.items() if schema.required and name not in self.params}

    def finalize(self, config):
        pass

    def validate(self, config, params: Optional[Dict[str, Any]] = None, subst: Optional[Dict[str, Any]] = None):
        pass

    def update_parameter(self, name, value):
        self.params[name] = value

    def make_substitition_namespace(self):
        ns = {name: str(value) for name, value in self.params.items()}
        ns.update(**{name: "MISSING" for name in self.missing_params})
        return OmegaConf.create(ns)


@dataclass 
class Cab(Cargo):
    """Represents a cab i.e. an atomic task in a recipe.
    See dataclass fields below for documentation of fields.

    Additional attributes available after validation with arguments:

        self.input_output:      combined parameter dict (self.input + self.output), maps name to Parameter
        self.missing_params:    dict (name to Parameter) of required parameters that have not been specified
    
    Raises:
        CabValidationError: [description]
    """
    image: Optional[str] = None                   # container image to run 
    command: str = MISSING                        # command to run (inside or outside the container)
    # not sure what these are
    msdir: Optional[bool] = False
    prefix: Optional[str] = "-"
    # cab management and cleanup definitions
    management: CabManagement = CabManagement()

    def __post_init__ (self):
        Cargo.__post_init__(self)
        if self.name is None:
            self.name = self.image or self.command.split()[0]
        for param in self.inputs.keys():
            if param in self.outputs:
                raise CabValidationError(f"cab {self.name}: parameter {param} is both an input and an output, this is not permitted")

    def validate(self, config, params: Optional[Dict[str, Any]] = None, subst: Optional[Dict[str, Any]] = None):
        self.params = validate_parameters(params, self.inputs_outputs, defaults=self.defaults, subst=subst)

    @property
    def summary(self):
        lines = [f"cab {self.name}:"] 
        for name, value in self.params.items():
            # if type(value) is validate.Error:
            #     lines.append(f"  {name} = ERR: {value}")
            # else:
            lines.append(f"  {name} = {value}")
                
        lines += [f"  {name} = ???" for name in self.missing_params.keys()]
        return lines


@dataclass
class Step:
    """Represents one processing step in a recipe"""
    cab: Optional[str] = None                       # if not None, this step is a cab and this is the cab name
    recipe: Optional["Recipe"] = None               # if not None, this step is a nested recipe
    params: Dict[str, Any] = EmptyDictDefault()     # assigns parameter values
    info: Optional[str] = None                      # comment or info

    _skip: Conditional = None                       # skip this step if conditional evaluates to true
    _break_on: Conditional = None                   # break out (of parent receipe) if conditional evaluates to true

    def __post_init__(self):
        if bool(self.cab) == bool(self.recipe):
            raise StepValidationError("step must specify either a cab or a nested recipe, but not both")
        self.cargo = None
        self._validated = None

    @property
    def summary(self):
        return self.cargo.summary

    @property
    def missing_params(self):
        return self.cargo.missing_params

    @property
    def invalid_params(self):
        return self.cargo.invalid_params

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
        if self.cargo is not None and self._validated:
            self.cargo.update_parameter(name, value)

    def finalize(self, config):
        if self.cargo is None:
            if bool(self.cab) == bool(self.recipe):
                raise StepValidationError("step must specify either a cab or a nested recipe, but not both")
            # if recipe, validate the recipe with our parameters
            if self.recipe:
                # instantiate from omegaconf object, if needed
                if type(self.recipe) is not Recipe:
                    self.recipe = Recipe(**self.recipe)
                self.cargo = self.recipe
            else:
                if self.cab not in config.cabs:
                    raise StepValidationError(f"unknown cab {self.cab}")
                self.cargo = Cab(**config.cabs[self.cab])
            self.cargo.finalize(config)

    def validate(self, config, subst: Optional[Dict[str, Any]] = None):
        # validate cab or receipe
        self.finalize(config)
        self.cargo.validate(config, self.params, subst=subst)
        self._validated = True
        self.params = self.cargo.params
        logger().debug(f"{self.cargo.name}: {len(self.missing_params)} missing and {len(self.invalid_params)} invalid parameters")
        if self.invalid_params:
            raise StepValidationError(f"{self.cargo.name} has the following invalid paramaters: {', '.join(self.invalid_params)}")


@dataclass
class Recipe(Cargo):
    """Represents a sequence of steps.

    Additional attributes available after validation with arguments are as per for a Cab:

        self.input_output:      combined parameter dict (self.input + self.output), maps name to Parameter
        self.missing_params:    dict (name to Parameter) of required parameters that have not been specified

    Raises:
        various classes of validation errors
    """
    steps: Dict[str, Step] = EmptyDictDefault()                # sequence of named steps

    dirs: Dict[str, Any] = EmptyDictDefault()       # I/O directory mappings

    vars: Dict[str, Any] = EmptyDictDefault()       # arbitrary collection of variables pertaining to this step (for use in substitutions)

    aliases: Dict[str, Any] = EmptyDictDefault()

    defaults: Dict[str, Any] = EmptyDictDefault()

    # loop over a set of variables
    _for: Optional[Dict[str, Any]] = None
    # if not None, do a while loop with the conditional
    _while: Conditional = None
    # if not None, do an until loop with the conditional
    _until: Conditional = None

    def __post_init__ (self):
        Cargo.__post_init__(self)
        for name, alias_list in self.aliases.items():
            if name in self.inputs_outputs:
                raise RecipeValidationError(f"alias {name} also appeards under inputs or outputs")
            if type(alias_list) is str:
                alias_list = self.aliases[name] = [alias_list]
            elif not isinstance(alias_list, (list, tuple)) and not all(type(x) is str for x in alias_list):
                raise RecipeValidationError(f"alias {name}: name or list of names expected")
        # instantiate steps if needed (when creating from an omegaconf)
        if type(self.steps) is not OrderedDict:
            steps = OrderedDict()
            for label, stepconfig in self.steps.items():
                steps[label] = Step(**stepconfig)
            self.steps = steps
        # map of aliases
        self._alias_map = None

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
                raise RecipeValidationError(f"alias {alias_name} refers to unknown parameter '{step_param_name}'")
        # check that it's not already set
        if step_param_name in step.params:
            raise RecipeValidationError(f"alias {alias_name} refers to already defined parameter '{step_param_name}'")
        # add to our mapping
        io = self.inputs if is_input else self.outputs
        existing_schema = io.get(alias_name)
        if existing_schema is None:                   
            io[alias_name] = schema.copy()
        else:
            # check if definition conflicts
            if bool(is_input) != bool(io is self.inputs) or schema.dtype != existing_schema.dtype:
                raise RecipeValidationError(f"alias {alias_name} has a conflicting list of definitions")
            # alias becomes required if any parm it refers to was required, unless recipe has a default
            if schema.required:
                existing_schema.required = True
        
        self._alias_map[step_label, step_param_name] = alias_name
        self._alias_list.setdefault(alias_name, []).append((step, step_param_name))


    def finalize(self, config):
        if self.finalized:
            return 

        # finalize step cargos
        for step in self.steps.values():
            step.finalize(config)

        # collect aliases
        self._alias_map = OrderedDict()
        self._alias_list = OrderedDict()

        for name, alias_list in self.aliases.items():
            for alias in alias_list:
                # verify mapped name
                step_label, step_param_name = alias.split('.', 1)
                step = self.steps.get(step_label)
                if step is None:
                    raise RecipeValidationError(f"alias {name} refers to unknown step '{step_label}'")
                self._add_alias(name, step_label, step, step_param_name)

        # automatically make aliases for unset required parameters 
        for label, step in self.steps.items():
            for name, schema in step.inputs_outputs.items():
                if (label, name) not in self._alias_map and name not in step.params and schema.required:
                    auto_name = f"{label}_{name}"
                    if auto_name in self.inputs or auto_name in self.outputs:
                        raise RecipeValidationError(f"auto-generated paramneter name '{auto_name}' conflicts with another name. Please define an explicit alias for this.")
                    self._add_alias(auto_name, step_label, step, name)
        
        # these will be re-merged when needed again
        self._inputs_outputs = None

    
    def validate(self, config, params: Optional[Dict[str, Any]] = None, subst: Optional[Dict[str, Any]] = None):
        logger().debug("validating recipe")
        try:
            self.finalize(config)
        except StimelaBaseException as exc:
            msg = f"error in recipe definition: {exc}"
            raise RecipeValidationError(msg, log=True)

        errors = []

        # we do this before validating steps, because steps may employ substitutions
        try:
            params = validate_parameters(params, self.inputs_outputs, defaults=self.defaults, subst=subst)
        except StimelaBaseException as exc:
            msg = f"recipe parameters failed to validate: {exc}"
            errors.append(RecipeValidationError(msg, log=True))

        # set values, this will also pass aliases up to substeps

        for name, value in params.items():
            self.update_parameter(name, value)

        if self.missing_params:
            msg = f"recipe '{self.name}' is missing the following required parameters: {', '.join(self.missing_params)}"
            errors.append(RecipeValidationError(msg, log=True))

        # validate step parameters 
        subst1 = subst.copy() if subst is not None else OmegaConf.create()
        subst1.recipe = self.make_substitition_namespace()
        subst1.steps  = OmegaConf.create()
        subst1.previous = None
        for label, step in self.steps.items():
            try:
                step.validate(config, subst=subst1)
            except StimelaBaseException as exc:
                msg = f"step '{label}' failed to validate: {exc}"
                errors.append(RecipeValidationError(msg, log=True))
            subst1.steps[label] = subst1.previous = step.cargo.make_substitition_namespace()


        if errors:
            raise RecipeValidationError(f"{len(errors)} error(s) validating the recipe '{self.name}'", log=True)

        return

    def update_parameter(self, name, value):
        self.params[name] = value
        for step, step_param_name in self._alias_list.get(name, []):
            step.update_parameter(step_param_name, value)


    @property
    def summary(self):
        lines = [f"recipe '{self.name}':"] + [f"  {name} = {value}" for name, value in self.params.items()] + \
                [f"  {name} = ???" for name in self.missing_params]
        lines.append("  steps:")
        for name, step in self.steps.items():
            stepsum = step.summary
            lines.append(f"    {name}: {stepsum[0]}")
            lines += [f"    {x}" for x in stepsum[1:]]
        return lines
