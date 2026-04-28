import configparser
from typing import ClassVar

from libresvip.model.vocaloid.controller_models import (
    ControllerCurve,
    ControllerEvent,
)
from libresvip.model.vocaloid.controller_registry import (
    get_param_def,
)


class VsqControllerAdapter:
    VSQ_PARAM_SECTIONS: ClassVar[dict[str, str]] = {
        "PitchBendBPList": "pitch_bend",
        "PitchBendSensBPList": "pitch_bend_sens",
        "DynamicsBPList": "dynamics",
        "GenderFactorBPList": "gender",
        "PortamentoTimingBPList": "portamento",
    }

    def __init__(self, tick_prefix: int = 0) -> None:
        self.tick_prefix = tick_prefix

    def extract_all(self, vsq_track: configparser.ConfigParser) -> list[ControllerCurve]:
        curves = []
        for section_name, param_name in self.VSQ_PARAM_SECTIONS.items():
            if vsq_track.has_section(section_name):
                curve = self._extract_from_section(vsq_track, section_name, param_name)
                if curve and not curve.is_empty():
                    curves.append(curve)
        return curves

    def extract(
        self, vsq_track: configparser.ConfigParser, param_name: str
    ) -> ControllerCurve | None:
        section_name = None
        for sec, pname in self.VSQ_PARAM_SECTIONS.items():
            if pname == param_name:
                section_name = sec
                break

        if section_name is None or not vsq_track.has_section(section_name):
            return None

        return self._extract_from_section(vsq_track, section_name, param_name)

    def _extract_from_section(
        self,
        vsq_track: configparser.ConfigParser,
        section_name: str,
        param_name: str,
    ) -> ControllerCurve | None:
        param_def = get_param_def(param_name)

        events = []
        for key, value in vsq_track[section_name].items():
            try:
                pos = int(key) - self.tick_prefix
                val = int(value)
                events.append(ControllerEvent(pos=pos, value=val))
            except (ValueError, TypeError):  # noqa: PERF203
                continue

        if not events:
            return None

        return ControllerCurve(
            name=param_name,
            events=events,
            default_value=param_def.default_value if param_def else 0,
            min_value=param_def.min_value if param_def else -127,
            max_value=param_def.max_value if param_def else 127,
        )

    def create_section(
        self,
        curve: ControllerCurve,
        vsq_track: configparser.ConfigParser,
    ) -> str | None:
        if curve.is_empty():
            return None

        section_name = None
        for sec, pname in self.VSQ_PARAM_SECTIONS.items():
            if pname == curve.name:
                section_name = sec
                break

        if section_name is None:
            section_name = f"{curve.name.capitalize()}BPList"

        if not vsq_track.has_section(section_name):
            vsq_track.add_section(section_name)

        for event in curve.events:
            vsq_track.set(section_name, str(event.pos + self.tick_prefix), str(event.value))

        return section_name


def extract_pitch_data(
    vsq_track: configparser.ConfigParser,
    tick_prefix: int = 0,
) -> tuple[ControllerCurve, ControllerCurve] | None:
    adapter = VsqControllerAdapter(tick_prefix=tick_prefix)

    pit_curve = adapter.extract(vsq_track, "pitch_bend")
    pbs_curve = adapter.extract(vsq_track, "pitch_bend_sens")

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
