from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class VocaloidParameterDef:
    name: str
    display_name: str
    vpr_name: str | None = None
    vsqx_name: str | None = None
    vsq_name: str | None = None
    min_value: int = -127
    max_value: int = 127
    default_value: int = 0
    is_complex: bool = False


VOCALOID_PARAMETERS: dict[str, VocaloidParameterDef] = {
    "pitch_bend": VocaloidParameterDef(
        name="pitch_bend",
        display_name="Pitch Bend",
        vpr_name="pitchBend",
        vsqx_name="P",
        vsq_name="PIT",
        min_value=-8192,
        max_value=8191,
        default_value=0,
        is_complex=True,
    ),
    "pitch_bend_sens": VocaloidParameterDef(
        name="pitch_bend_sens",
        display_name="Pitch Bend Sensitivity",
        vpr_name="pitchBendSens",
        vsqx_name="S",
        vsq_name="PBS",
        min_value=1,
        max_value=24,
        default_value=2,
        is_complex=True,
    ),
    "dynamics": VocaloidParameterDef(
        name="dynamics",
        display_name="Dynamics",
        vpr_name="dynamics",
        vsqx_name="D",
        vsq_name="DYN",
        min_value=0,
        max_value=127,
        default_value=64,
    ),
    "breathiness": VocaloidParameterDef(
        name="breathiness",
        display_name="Breathiness",
        vpr_name="breathiness",
        vsqx_name="B",
        vsq_name="BRE",
        default_value=0,
    ),
    "brightness": VocaloidParameterDef(
        name="brightness",
        display_name="Brightness",
        vpr_name="brightness",
        vsqx_name="R",
        vsq_name="BRI",
        default_value=0,
    ),
    "gender": VocaloidParameterDef(
        name="gender",
        display_name="Gender Factor",
        vpr_name="gender",
        vsqx_name="G",
        vsq_name="GEN",
        default_value=0,
    ),
}


def get_param_def(name: str) -> VocaloidParameterDef | None:
    return VOCALOID_PARAMETERS.get(name)


def get_param_by_format(
    format_name: Literal["vpr", "vsqx", "vsq"],
    param_id: str,
) -> VocaloidParameterDef | None:
    attr_name = f"{format_name}_name"
    for param in VOCALOID_PARAMETERS.values():
        if getattr(param, attr_name) == param_id:
            return param
    return None
