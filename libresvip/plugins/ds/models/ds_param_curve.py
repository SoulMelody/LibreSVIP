from dataclasses import dataclass, field

from .ds_param_node import DsParamNode


@dataclass
class DsParamCurve:
    step_size: float = 0.005
    point_list: list[DsParamNode] = field(default_factory=list)
