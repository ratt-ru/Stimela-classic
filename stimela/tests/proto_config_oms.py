import glob
import re
import os.path
import sys
from collections.abc import Sequence
from collections import OrderedDict

from omegaconf.errors import ValidationError

import stimela


from omegaconf.omegaconf import MISSING, OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
from typing import Any, List, Dict, Optional, Union
from enum import Enum
import dataclasses
from dataclasses import dataclass

import pydantic.dataclasses
from pydantic import ValidationError

from stimela.config import Parameter, EmptyListDefault, EmptyDictDefault


class MyConfig:
    pass

class File(str):
    pass

if __name__ == "__main__":

    from pydantic import BaseModel

    parmlist = OrderedDict()

    parmlist['foo'] = Parameter(dtype='str')
    parmlist['bar'] = Parameter(dtype='Optional[Union[int,float]]')
    parmlist['x'] = Parameter(dtype='File')
    parmlist['y'] = Parameter(dtype='Union[str,List[str]]')

    fields = []
    for name, param in parmlist.items():
        dtype = eval(param.dtype, globals())
        fields.append((name, dtype))
    print(fields)

    dcls = dataclasses.make_dataclass("MyClass", fields)
    pcls = pydantic.dataclasses.dataclass(dcls)
#    pcls = pydantic.dataclasses.make_dataclass_validator(dcls, MyConfig)

    # for p in pcls:
    #     print(p)

    print(pcls(foo='xxx', bar='123', x='a', y=[]))

    print(pcls(foo='xxx', bar=None, x=1, y=[1,2,3]))

    print(pcls(foo='xxx', bar=None, x=1, y='a'))

    try:   
        print(pcls(foo=None, bar=None, x=0, y=0))
    except ValidationError as exc:
        print(f"validation error as expected: {exc}")
 