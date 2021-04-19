from collections import OrderedDict
import dataclasses

from omegaconf.omegaconf import OmegaConf
import pydantic
import pydantic.dataclasses

from stimela.exceptions import ParameterValidationError, SchemaError
from typing import *

class File(str):
    pass

class Directory(str):
    pass

class MS(Directory):
    pass

class Error(str):
    pass

def validate_schema(schema: Dict[str, Any]):
    """Checks a set of parameter schemas for internal consistency.

    Args:
        schema (Dict[str, Any]):   dict of parameter schemas

    Raises:
        SchemaError: [description]
    """

    pass



def validate_parameters(params: Dict[str, Any], schema: Dict[str, Any], 
                        subst: Optional[Dict[str, Any]] = None,
                        use_defaults=True) -> Dict[str, Any]:
    """Validates a dict of parameter values against a given schema 

    Args:
        params (Dict[str, Any]):   map of input parameter values
        schema (Dict[str, Any]):   map of parameter names to schemas. Each schema must contain a dtype field and a choices field.
        subst  (Dict[str, Any], optional): dictionary of substitutions to be made in str-valued parameters (using .format(**subst))
        use_defaults (bool):       if true, output dict will include default values from schema where a value is missing in the input

    Raises:
        ParameterValidationError: [description]
        SchemaError: [description]
        ParameterValidationError: [description]

    Returns:
        Dict[str, Any]: validated dict of parameters

    TODO:
        add options to propagate all errors out (as values of type Error) in place of exceptions?
    """
    # check for unknowns
    for name in params:
        if name not in schema:
            raise ParameterValidationError(f"unknown parameter {name}")

    # omegaconf's DictConfig objects don't support derived types such as validation.Error, so for the purpose of
    # substitutions, convert the params into a regular dict first
    inputs = dict(**params)

    # add missing defaults and/or implicit parameters
    for name, parmdef in schema.items():
        if name in inputs:
            if parmdef.implicit is not None:
                raise ParameterValidationError(f"implicit parameter {name} was supplied excplicitly")
        else:
            if parmdef.implicit is not None:
                inputs[name] = parmdef.implicit
            elif use_defaults and parmdef.default is not None and not parmdef.required:
                inputs[name] = parmdef.default

    # do substitutions if asked to
    # since substitutions can potentially reference each other, repeat this until things sette
    if subst is not None:
        # substitution namespace is input dict plus current parameter values
        subst1 = subst.copy()
        subst1_self = subst1['self'] = OmegaConf.create(inputs)
        for i in range(10):
            changed = False
            # loop over parameters and find ones to substitute
            for name, value in inputs.items():
                if isinstance(value, str) and not isinstance(value, Error):
                    try:
                        newvalue = value.format(**subst1)
                        subst1_self[name] = str(newvalue)
                    except Exception as exc:
                        newvalue = Error(f"{{{exc}}}")
                        subst1_self[name] = "ERR"
                    if newvalue != value:
                        inputs[name] = newvalue
                        changed = True
            if not changed:
                break 
        else:
            raise ParameterValidationError("recursion limit exceeded while evaluating {}-substitutions. This is usally caused by cyclic (cross-)references.")
    else:
        inputs = params.copy()

    # create dataclass from parameter schema
    fields = []
    for name, parmdef in schema.items():
        if name not in inputs:
            if not use_defaults or parmdef.required or parmdef.default is None:
                continue
            inputs[name] = parmdef.default
        try:
            dtype = eval(parmdef.dtype, globals())
        except Exception as exc:
            raise SchemaError(f"invalid {name}.dtype={parmdef.dtype}")
        fields.append((name, dtype))

    dcls = dataclasses.make_dataclass("Parameters", fields)
    
    # convert this to a pydantic dataclass which does validation
    pcls = pydantic.dataclasses.dataclass(dcls)

    # validate
    try:   
        validated = pcls(**inputs)
    except pydantic.ValidationError as exc:
        raise ParameterValidationError(f"{exc}")

    ## TODO: check "choices" field

    return dataclasses.asdict(validated)
