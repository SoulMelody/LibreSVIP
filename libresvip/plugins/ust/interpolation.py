from libresvip.model.pitch import CurveShape

from .model import UTAUPitchBendMode

# UTAU names its bend modes after the resulting shape rather than the easing
# curve, and an empty mode means the default ease-in-out. Mapping lives here so
# the shared semantics layer only ever sees `CurveShape`.
UTAU_CURVE_SHAPES: dict[UTAUPitchBendMode, CurveShape] = {
    "s": CurveShape.LINEAR,
    "j": CurveShape.EASE_IN,
    "r": CurveShape.EASE_OUT,
    "": CurveShape.EASE_IN_OUT,
}


def utau_curve_shape(mode: UTAUPitchBendMode) -> CurveShape:
    return UTAU_CURVE_SHAPES[mode]
