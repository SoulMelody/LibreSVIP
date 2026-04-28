from libresvip.model.vocaloid.controller_models import (
    ControllerCurve,
    ControllerEvent,
)
from libresvip.model.vocaloid.controller_registry import (
    get_param_by_format,
    get_param_def,
)

from .model import VocaloidControllers, VocaloidPoint, VocaloidVoicePart


class VprControllerAdapter:
    def extract_all(self, part: VocaloidVoicePart) -> list[ControllerCurve]:
        curves = []
        if part.controllers:
            for controller in part.controllers:
                curve = self._convert_to_curve(controller)
                if curve and not curve.is_empty():
                    curves.append(curve)
        return curves

    def extract(self, part: VocaloidVoicePart, param_name: str) -> ControllerCurve | None:
        param_def = get_param_def(param_name)
        if not param_def or not param_def.vpr_name:
            return None

        for controller in part.controllers or []:
            if controller.name == param_def.vpr_name:
                return self._convert_to_curve(controller)
        return None

    def extract_by_vpr_name(self, part: VocaloidVoicePart, vpr_name: str) -> ControllerCurve | None:
        for controller in part.controllers or []:
            if controller.name == vpr_name:
                return self._convert_to_curve(controller)
        return None

    def _convert_to_curve(self, controller: VocaloidControllers) -> ControllerCurve | None:
        if controller.name is None:
            return None
        param_def = get_param_by_format("vpr", controller.name)

        if param_def:
            name = param_def.name
            default_value = param_def.default_value
            min_value = param_def.min_value
            max_value = param_def.max_value
        else:
            name = controller.name
            default_value = 0
            min_value = -127
            max_value = 127

        events = [
            ControllerEvent(pos=event.pos, value=int(event.value))
            for event in controller.events
            if event.value is not None
        ]

        return ControllerCurve(
            name=name,
            events=events,
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
        )

    def create(self, curve: ControllerCurve) -> VocaloidControllers | None:
        if curve.is_empty():
            return None

        param_def = get_param_def(curve.name)
        vpr_name = param_def.vpr_name if param_def else curve.name

        events = [VocaloidPoint(pos=event.pos, value=event.value) for event in curve.events]

        return VocaloidControllers(name=vpr_name, events=events)

    def create_multiple(self, curves: list[ControllerCurve]) -> list[VocaloidControllers]:
        return [controller for curve in curves if (controller := self.create(curve))]


def extract_pitch_data(part: VocaloidVoicePart) -> tuple[ControllerCurve, ControllerCurve] | None:
    adapter = VprControllerAdapter()

    pit_curve = adapter.extract(part, "pitch_bend")
    pbs_curve = adapter.extract(part, "pitch_bend_sens")

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


def create_pitch_controllers(
    pit_curve: ControllerCurve,
    pbs_curve: ControllerCurve,
) -> list[VocaloidControllers]:
    adapter = VprControllerAdapter()
    controllers = []

    if pit_controller := adapter.create(pit_curve):
        controllers.append(pit_controller)

    if pbs_controller := adapter.create(pbs_curve):
        controllers.append(pbs_controller)

    return controllers


VPR_PARAM_NAMES = {
    "pitch_bend": "pitchBend",
    "pitch_bend_sens": "pitchBendSens",
    "dynamics": "dynamics",
    "breathiness": "breathiness",
    "brightness": "brightness",
    "clearness": "clearness",
    "gender": "gender",
    "portamento": "portamento",
    "cross_synth": "crossSynthesis",
    "growl": "growl",
}
