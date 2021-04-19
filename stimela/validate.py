from collections import OrderedDict
import dataclasses
import pydantic
import pydantic.dataclasses

from stimela.exceptions import ParameterValidationError, SchemaError
from typing import *

class File(str):
    pass

class Directory(str):
    pass


def validate_schema(schema: Dict[str, Any]):
    """Checks a parameter schema for consistency.

    Args:
        schema (Dict[str, Any]):   parameter schema

    Raises:
        SchemaError: [description]
    """

    pass


def validate_parameters(params: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validates a dict of parameter values against the schema 

    Args:
        params (Dict[str, Any]):   map of parameter values
        schema (Dict[str, Any]):   map of parameter names to schemas. Each schema must contain a dtype field and a choices field.

    Raises:
        ParameterValidationError: [description]
        SchemaError: [description]
        ParameterValidationError: [description]

    Returns:
        Dict[str, Any]: validated dict of parameters
    """
    # create dataclass from parameter schema
    fields = []
    for name in params:
        param = schema[name]
        parmdef = schema.get(name)
        if parmdef is None:
            raise ParameterValidationError(f"unknown parameter {name}")
        try:
            dtype = eval(parmdef.dtype, globals())
        except Exception as exc:
            raise SchemaError(f"invalid {name}.dtype = {param.dtype}")
        fields.append((name, dtype))

    dcls = dataclasses.make_dataclass("Parameters", fields)
    
    # convert this to a pydantic dataclass which does validation
    pcls = pydantic.dataclasses.dataclass(dcls)

    # overwrite default values and validate
    try:   
        validated = pcls(**params)
    except pydantic.ValidationError as exc:
        raise ParameterValidationError(f"{exc}")

    ## TODO: check "choices" field

    # return dictionay of values
    return dataclasses.asdict(validated)
