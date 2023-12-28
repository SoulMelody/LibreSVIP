from dataclasses import dataclass
from typing import Optional

from .ds_param_node import DsParamNode


@dataclass
class DsParamCurve:
    step_size: float = 0.005
    point_list: Optional[list[DsParamNode]] = None
