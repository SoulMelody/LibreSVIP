from typing import ClassVar

from libresvip.model.vocaloid.controller_models import (
    ControllerCurve,
    ControllerEvent,
)
from libresvip.model.vocaloid.controller_registry import (
    get_param_def,
)

from .model import VsqBPList, VsqMetaText


class XvsqControllerAdapter:
    XVSQ_PARAM_MAP: ClassVar[dict[str, str]] = {
        "dyn": "dynamics",
        "bre": "breathiness",
        "bri": "strength",
        "gen": "gender",
    }

    def __init__(self, tick_prefix: int = 0) -> None:
        self.tick_prefix = tick_prefix

    def extract(self, meta_text: VsqMetaText, param_name: str) -> ControllerCurve | None:
        param_def = get_param_def(param_name)
        if param_def is None:
            return None

        xvsq_param_name = None
        for xname, pname in self.XVSQ_PARAM_MAP.items():
            if pname == param_name:
                xvsq_param_name = xname
                break

        if xvsq_param_name is None:
            return None

        bplist = getattr(meta_text, xvsq_param_name, None)
        if bplist is None or not isinstance(bplist, VsqBPList):
            return None

        points = bplist.points
        if not points:
            return None

        events = [
            ControllerEvent(pos=int(point.x) - self.tick_prefix, value=point.y) for point in points
        ]

        if not events:
            return None

        return ControllerCurve(
            name=param_name,
            events=events,
            default_value=param_def.default_value,
            min_value=param_def.min_value,
            max_value=param_def.max_value,
        )

    def create_bplist(
        self,
        curve: ControllerCurve,
    ) -> tuple[str, VsqBPList] | None:
        if curve.is_empty():
            return None

        xvsq_param_name = None
        for xname, pname in self.XVSQ_PARAM_MAP.items():
            if pname == curve.name:
                xvsq_param_name = xname
                break

        if xvsq_param_name is None:
            return None

        param_def = get_param_def(curve.name)
        default_value = param_def.default_value if param_def else 0
        min_value = param_def.min_value if param_def else 0
        max_value = param_def.max_value if param_def else 127

        from .model import VibratoBPPair

        points = [
            VibratoBPPair(x=event.pos + self.tick_prefix, y=event.value) for event in curve.events
        ]

        bplist = VsqBPList(
            default=default_value,
            name=xvsq_param_name,
            maximum=max_value,
            minimum=min_value,
        )
        bplist.points = points

        return xvsq_param_name, bplist


def extract_pitch_data(
    meta_text: VsqMetaText,
    tick_prefix: int = 0,
) -> tuple[ControllerCurve, ControllerCurve] | None:
    pit_points = meta_text.pit.points if meta_text.pit else []
    pbs_points = meta_text.pbs.points if meta_text.pbs else []

    if not pit_points:
        return None

    pit_events = [
        ControllerEvent(pos=int(point.x) - tick_prefix, value=point.y) for point in pit_points
    ]

    pbs_events = [
        ControllerEvent(pos=int(point.x) - tick_prefix, value=point.y) for point in pbs_points
    ]

    pit_curve = ControllerCurve(
        name="pitch_bend",
        events=pit_events,
        default_value=0,
        min_value=-8192,
        max_value=8191,
    )

    if not pbs_events:
        pbs_curve = ControllerCurve(
            name="pitch_bend_sens",
            events=[],
            default_value=2,
            min_value=1,
            max_value=24,
        )
    else:
        pbs_curve = ControllerCurve(
            name="pitch_bend_sens",
            events=pbs_events,
            default_value=2,
            min_value=1,
            max_value=24,
        )

    return pit_curve, pbs_curve
