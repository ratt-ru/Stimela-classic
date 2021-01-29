from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Union


@dataclass
class StimelaImageBuildInfo:
    stimela_version: str = ""
    user: str = ""
    date: str = ""
    host: str = ""  

@dataclass
class StimelaImageInfo:
    name: str = ""
    version: str = ""
    full_name: str = ""
    iid: str = ""
    build: Union[StimelaImageBuildInfo, None] = None

