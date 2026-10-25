"""Format-agnostic pitch-curve operations.

Curves travel between engines as `list[Point]` at project-absolute ticks, and
every engine needs the same three operations on them: sampling one shape down to
a fixed interval, simplifying a dense run back to few anchors, and drawing the
intermediate samples of one segment with a particular easing.

They live here rather than in a plugin because nothing about them is
format-specific — the first two were reachable only from UTAU's code path even
though any adapter could use them. Plugins keep ownership of their own
vocabulary (UTAU's `s`/`j`/`r` bend modes, USTX's `lo`/`i`/`o`/`io`/`sp` shape
strings) and map it onto [`CurveShape`] at the call site.

Hard rules for code in this package:

* signatures take narrow types (`list[Point]`) — never `Project` or
  `SingingTrack`, so a plugin cannot smuggle project state in;
* time is project-absolute ticks;
* no new point types: curves are `list[Point]` (or `ParamCurve` at the boundary).
"""

from .interpolation import CurveShape, interpolate
from .rdp import perpendicular_distance, simplify_shape, simplify_shape_to
from .resampling import dot_resampled, resampled

__all__ = [
    "CurveShape",
    "dot_resampled",
    "interpolate",
    "perpendicular_distance",
    "resampled",
    "simplify_shape",
    "simplify_shape_to",
]
