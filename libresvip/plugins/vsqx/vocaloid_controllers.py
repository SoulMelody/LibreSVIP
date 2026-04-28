from typing import TYPE_CHECKING, Any

from libresvip.model.vocaloid.controller_models import (
    ControllerCurve,
    ControllerEvent,
)
from libresvip.model.vocaloid.controller_registry import (
    get_param_by_format,
    get_param_def,
)

if TYPE_CHECKING:
    from .model import VsqxMusicalPart


class VsqxControllerAdapter:
    def __init__(self, param_names: type) -> None:
        self.param_names = param_names

    def extract_all(self, musical_part: "VsqxMusicalPart") -> list[ControllerCurve]:
        curves = []
        events_by_param: dict[str, list[ControllerEvent]] = {}

        for m_ctrl in musical_part.m_ctrl:
            if m_ctrl.attr is None or m_ctrl.attr.type_param_attr_id is None:
                continue

            param_id = m_ctrl.attr.type_param_attr_id
            param_def = get_param_by_format("vsqx", param_id)

            if param_def is None:
                continue

            param_name = param_def.name
            if param_name not in events_by_param:
                events_by_param[param_name] = []

            if m_ctrl.attr.value is not None:
                events_by_param[param_name].append(
                    ControllerEvent(
                        pos=m_ctrl.pos_tick,
                        value=m_ctrl.attr.value,
                    )
                )

        for param_name, events in events_by_param.items():
            if not events:
                continue

            param_def = get_param_def(param_name)
            curve = ControllerCurve(
                name=param_name,
                events=events,
                default_value=param_def.default_value if param_def else 0,
                min_value=param_def.min_value if param_def else -127,
                max_value=param_def.max_value if param_def else 127,
            )
            curves.append(curve)

        return curves

    def extract(self, musical_part: "VsqxMusicalPart", param_name: str) -> ControllerCurve | None:
        param_def = get_param_def(param_name)
        if param_def is None or param_def.vsqx_name is None:
            return None

        vsqx_param_id = param_def.vsqx_name

        events = [
            ControllerEvent(
                pos=m_ctrl.pos_tick,
                value=m_ctrl.attr.value,
            )
            for m_ctrl in musical_part.m_ctrl
            if (
                m_ctrl.attr is not None
                and m_ctrl.attr.type_param_attr_id == vsqx_param_id
                and m_ctrl.attr.value is not None
            )
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

    def create_mctrl_list(
        self,
        curve: ControllerCurve,
        mctrl_class: type,
    ) -> list[Any]:
        if curve.is_empty():
            return []

        param_def = get_param_def(curve.name)
        vsqx_param_id = param_def.vsqx_name if param_def else curve.name

        mctrl_list = []
        for event in curve.events:
            mctrl = mctrl_class(
                pos_tick=event.pos,
                attr=mctrl_class.__dataclass_fields__["attr"].type(
                    type_param_attr_id=vsqx_param_id,
                    value=event.value,
                ),
            )
            mctrl_list.append(mctrl)

        return mctrl_list


def extract_pitch_data(
    musical_part: "VsqxMusicalPart",
    param_names: type,
) -> tuple[ControllerCurve, ControllerCurve] | None:
    adapter = VsqxControllerAdapter(param_names=param_names)

    pit_curve = adapter.extract(musical_part, "pitch_bend")
    pbs_curve = adapter.extract(musical_part, "pitch_bend_sens")

    if pit_curve is None:
        return None

    if pbs_curve is None:
        pbs_curve = ControllerCurve(
            name="pitch_bend_sens",
            events=[],
            default_value=2,
            min_value=1,
            max_value=24,
        )

    return pit_curve, pbs_curve
