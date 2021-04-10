import glob
import os, os.path
from typing import Any, List, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from omegaconf.omegaconf import MISSING, OmegaConf, DictConfig
from collections import OrderedDict
from stimela.config import EmptyDictDefault, EmptyListDefault, Parameter, CabManagement
from stimela.validate import validate_parameters
from stimela import logger

from stimela.exceptions import *

Conditional = Optional[str]



def _collect_missing_parameters(params, inputs_outputs):
    # validate each parameter
    for name, value in params.items():
        if name not in inputs_outputs:
            raise ParameterValidationError(f"parameter {name} is unknown")
        ## here be type checking and that kind of stuff

    missing = OrderedDict()

    # collect dict of missing mandatory parameters
    for name, param in inputs_outputs.items():
        if param.required and name not in params:
            missing[name] = param

    return missing



@dataclass 
class Cab(object):
    """Represents a cab i.e. an atomic task in a recipe.
    See dataclass fields below for documentation of fields.

    Additional attributes available after validation with arguments:

        self.input_output:      combined parameter dict (self.input + self.output), maps name to Parameter
        self.missing_params:    dict (name to Parameter) of required parameters that have not been specified
    
    Raises:
        CabValidationError: [description]
    """
    name: Optional[str] = None                    # cab name. (If None, use image or command name)
    info: Optional[str] = None                    # description
    image: Optional[str] = None                   # container image to run 
    command: str = MISSING                        # command to run (inside or outside the container)
    # not sure what these are
    msdir: Optional[bool] = False
    prefix: Optional[str] = "-"
    # cab management and cleanup definitions
    management: CabManagement = CabManagement()
    # cab parameter definitions
    inputs: Dict[str, Parameter] = EmptyDictDefault()
    outputs: Dict[str, Parameter] = EmptyDictDefault()

    def __post_init__ (self):
        if self.name is None:
            self.name = self.image or self.command.split()[0]
        for param in self.inputs.keys():
            if param in self.outputs:
                raise CabValidationError(f"cab {self.name}: parameter {name} is both an input and an output, this is not permitted")


    def validate(self, config, params: Optional[Dict[str, Any]] = None):
        # create merged param dict
        self.inputs_outputs = self.inputs.copy()
        self.inputs_outputs.update(**self.outputs)
        # collect missing required parameters
        self.params = validate_parameters(params, self.inputs_outputs)
        self.missing_params = _collect_missing_parameters(params, self.inputs_outputs)
        logger().debug(f"cab {self.name} is missing {len(self.missing_params)} required parameters")

    def update_parameter(self, name, value):
        self.params[name] = value
        if name in self.missing_params:
            del self.missing_params[name]

    @property
    def summary(self):
        lines = [f"cab {self.name}:"] + [f"  {name} = {value}" for name, value in self.params.items()] + \
                [f"  {name} = ???" for name in self.missing_params.keys()]
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


    @property
    def summary(self):
        return self.cargo.summary

    @property
    def missing_params(self):
        return self.cargo.missing_params

    @property
    def inputs(self):
        return self.cargo.inputs

    @property
    def outputs(self):
        return self.cargo.outputs

    @property
    def inputs_outputs(self):
        return self.cargo.inputs_outputs

    def validate(self, config):
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
                raise StepValidationError("unknown cab {self.cab}")
            self.cargo = Cab(**config.cabs[self.cab])
        # validate cab or receipe
        self.cargo.validate(config, self.params)
        logger().debug(f"step is missing {len(self.missing_params)} required parameters")


@dataclass
class Recipe:
    """Represents a sequence of steps.

    Additional attributes available after validation with arguments are as per for a Cab:

        self.input_output:      combined parameter dict (self.input + self.output), maps name to Parameter
        self.missing_params:    dict (name to Parameter) of required parameters that have not been specified

    Raises:
        various classes of validation errors
    """
    name: str = ""
    info: str = ""
    steps: Dict[str, Step] = EmptyDictDefault()                # sequence of named steps

    dirs: Dict[str, Any] = EmptyDictDefault()       # I/O directory mappings

    vars: Dict[str, Any] = EmptyDictDefault()       # arbitrary collection of variables pertaining to this step (for use in substitutions)

    # Formally defines the recipe's inputs and outputs
    # See discussion in https://github.com/ratt-ru/Stimela/discussions/698#discussioncomment-362273
    # If None, these are inferred automatically from the steps' parameters
    inputs: Dict[str, Parameter] = EmptyDictDefault()
    outputs: Dict[str, Parameter] = EmptyDictDefault()

    # loop over a set of variables
    _for: Optional[Dict[str, Any]] = None
    # if not None, do a while loop with the conditional
    _while: Conditional = None
    # if not None, do an until loop with the conditional
    _until: Conditional = None

    def __post_init__ (self):
        for param in self.inputs.keys():
            if param in self.outputs:
                raise CabValidationError(f"cab {self.name}: parameter {name} is both an input and an output, this is not permitted")
        for io in self.inputs, self.outputs:
            for name, param in io.items():
                for maps in param.maps_to:
                    if '.' not in maps:
                        raise RecipeValidationError(f"parameter {name}.maps_to: '{maps}' is missing a step name")
        # instantiate steps if needed (when creating from an omegaconf)
        if type(self.steps) is not OrderedDict:
            steps = OrderedDict()
            for label, stepconfig in self.steps.items():
                steps[label] = Step(**stepconfig)
            self.steps = steps

    def add(self, step: Step, label: str=None):
        """Adds a step to the recipe. Label is auto-generated if not supplied

        Args:
            step (Step): step object to add
            label (str, optional): step label, auto-generated if None
        """
        self.steps[label or f"step_{len(self.steps)}"] = step

    
    def validate(self, config, params: Optional[Dict[str, Any]] = None):
        logger().debug("validating recipe")
        # create merged param dict
        self.inputs_outputs = self.inputs.copy()
        self.inputs_outputs.update(**self.outputs)

        # collect missing parameters from steps
        # this dict will be used to auto-generate recipe parameters based on required step parameters that are
        # not explicitly set in the step
        auto_params = OrderedDict()             # maps name to (Parameter, is_input: bool)
        for label, step in self.steps.items():
            try:
                step.validate(config)
            except StimelaBaseException as exc:
                raise RecipeValidationError(f"step {label} failed to validate: {exc}")
            for name, param in step.missing_params.items():
                auto_params[f"{label}.{name}"] = param, (name in step.inputs)
        
        # these auto-generated params need to be promoted to our own inputs/outputs, 
        # _unless_ we already have an explicitly defined input or output that maps it anyway
        for name, param in self.inputs_outputs.items():
            is_input = name in self.inputs
            for maps in param.maps_to:
                # verify mapped name
                step_label, step_param_name = maps.split('.', 1)
                step = self.steps.get(step_label)
                if step is None:
                    raise RecipeValidationError(f"parameter {name}.maps_to unknown step '{step_label}'")
                step_param = (step.inputs if is_input else step.outputs).get(step_param_name)
                if step_param is None:
                    raise RecipeValidationError(f"parameter {name}.maps_to unknown parameter '{maps}'")
                # if step's parameter is a required one, so should this one be
                if step_param.required:
                    param.required = True
                ## TODO: check that types are consistent between this type and the step parameter type
                # delete from auto dict, if in it
                if maps in auto_params:
                    del auto_params[maps]
                # else check that it is legit, and not already assigned to
                elif step_param_name in step.params:
                    raise RecipeValidationError(f"parameter {name}.maps_to '{maps}', but the mapped parameter is already set explicitly")
        
        # anything left becomes a recipe parameter
        for name, (param, is_input) in auto_params.items():
            (self.inputs if is_input else self.outputs)[name] = self.inputs_outputs[name] = param

        logger().debug(f"recipe parameters are: {' '.join(self.inputs_outputs.keys())}")

        # now validate our own inputs and outputs against supplied values
        self.params = validate_parameters(params or OrderedDict(), self.inputs_outputs)
        self.missing_params = _collect_missing_parameters(self.params, self.inputs_outputs)

        # any parameters that map to step parameters now need to be propagated back to the step
        for name, value in self.params.items():
            self.update_parameter(name, value)

        logger().debug(f"recipe is missing {len(self.missing_params)} required parameters")

    def update_parameter(self, name, value):
        param = self.inputs.get(name) or self.outputs.get(name)
        for maps in param.maps_to:
            step_label, step_param_name = maps.split('.', 1)
            step = self.steps.get(step_label)
            if step is None:
                raise RecipeValidationError(f"parameter {name}.maps_to unknown step '{step_label}'")
            if step_param_name not in step.inputs_outputs:
                raise RecipeValidationError(f"parameter {name}.maps_to unknown parameter '{maps}'")
            step.cargo.update_parameter(step_param_name, value)
        self.params[name] = value

    @property
    def summary(self):
        lines = [f"recipe '{self.name}':"] + [f"  {name} = {value}" for name, value in self.params.items()] + \
                [f"  {name} = ???" for name in self.missing_params.keys()]
        lines.append("  steps:")
        for name, step in self.steps.items():
            stepsum = step.summary
            lines.append(f"    {name}: {stepsum[0]}")
            lines += [f"    {x}" for x in stepsum[1:]]
        return lines





