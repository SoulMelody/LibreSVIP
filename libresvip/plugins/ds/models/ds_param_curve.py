from dataclasses import dataclass

from .ds_param_node import DsParamNode


@dataclass
class DsParamCurve:
    step_size: float = 0.005
    point_list: list[DsParamNode] | None = None
