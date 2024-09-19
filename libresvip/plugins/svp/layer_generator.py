import dataclasses
import math
from collections.abc import Callable
from typing import NamedTuple

import more_itertools

from libresvip.core.exceptions import NotesOverlappedError, ParamsError
from libresvip.utils.music_math import clamp
from libresvip.utils.search import find_index
from libresvip.utils.translation import gettext_lazy as _

from .constants import MAX_BREAK
from .lambert_w import LambertW


class NoteStruct(NamedTuple):
    key: int
    start: float
    end: float
    portamento_offset: float
    portamento_left: float
    portamento_right: float
    depth_left: float
    depth_right: float
    vibrato_start: float
    vibrato_left: float
    vibrato_right: float
    vibrato_depth: float
    vibrato_frequency: float
    vibrato_phase: float


@dataclasses.dataclass
class SigmoidNode:
    start: float = dataclasses.field(init=False)
    end: float = dataclasses.field(init=False)
    center: float = dataclasses.field(init=False)
    sigmoid_l: Callable[[float], float] = dataclasses.field(init=False)
    sigmoid_r: Callable[[float], float] = dataclasses.field(init=False)
    d_sigmoid_l: Callable[[float], float] = dataclasses.field(init=False)
    d_sigmoid_r: Callable[[float], float] = dataclasses.field(init=False)
    _start: dataclasses.InitVar[float]
    _end: dataclasses.InitVar[float]
    _center: dataclasses.InitVar[float]
    _radius: dataclasses.InitVar[float]
    _key_left: dataclasses.InitVar[int]
    _key_right: dataclasses.InitVar[int]

    @property
    def k(self) -> float:
        return 5.5

    def __post_init__(
        self,
        _start: float,
        _end: float,
        _center: float,
        _radius: float,
        _key_left: int,
        _key_right: int,
    ) -> None:
        self.start = _start
        self.end = _end
        self.center = _center
        h: float = (_key_right - _key_left) * 100
        a = 1 / (1 + math.exp(self.k))
        power = 0.75

        left = self.center - self.start
        if left >= _radius or left == 0:
            k_l = self.k
            h_l = h
            d_l = 0.0
        else:
            al = a * math.pow(_radius / left, power)
            bl = left / _radius
            cl = al * bl * self.k / (2 * al - 1)
            k_l = al / (2 * al - 1) * self.k - 1 / bl * LambertW.evaluate(cl * math.exp(cl), -1)
            h_l = h * k_l / (2 * k_l - self.k)
            d_l = -_radius / k_l * math.log(2 * h_l / h - 1)

        self.sigmoid_l = lambda x: _key_left * 100 + h_l / (
            1 + math.exp(-k_l / _radius * (x - self.center + d_l))
        )
        self.d_sigmoid_l = (
            lambda x: h_l
            * k_l
            / _radius
            * math.exp(-k_l / _radius * (x - self.center + d_l))
            / math.pow(1 + math.exp(-k_l / _radius * (x - self.center + d_l)), 2)
        )

        right = self.end - self.center
        if right >= _radius or right == 0:
            k_r = self.k
            h_r = h
            d_r = 0.0
        else:
            ar = a * math.pow(_radius / right, power)
            br = right / _radius
            cr = ar * br * self.k / (2 * ar - 1)
            k_r = ar / (2 * ar - 1) * self.k - 1 / br * LambertW.evaluate(cr * math.exp(cr), -1)
            h_r = h * k_r / (2 * k_r - self.k)
            d_r = -_radius / k_r * math.log(2 * h_r / h - 1)

        self.sigmoid_r = lambda x: _key_right * 100 - h_r / (
            1 + math.exp(-k_r / _radius * (self.center - x + d_r))
        )
        self.d_sigmoid_r = (
            lambda x: h_r
            * k_r
            / _radius
            * math.exp(-k_r / _radius * (self.center - x + d_r))
            / math.pow(1 + math.exp(-k_r / _radius * (self.center - x + d_r)), 2)
        )

    def value_at_secs(self, secs: float) -> float:
        return self.sigmoid_l(secs) if secs <= self.center else self.sigmoid_r(secs)

    def slope_at_secs(self, secs: float) -> float:
        return self.d_sigmoid_l(secs) if secs <= self.center else self.d_sigmoid_r(secs)


@dataclasses.dataclass
class BaseLayerGenerator:
    default_radius = 0.07
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    note_list: list[NoteStruct] = dataclasses.field(init=False)
    sigmoid_nodes: list[SigmoidNode] = dataclasses.field(default_factory=list)

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        if not _note_list:
            return
        self.note_list = _note_list
        for current_note, next_note in more_itertools.pairwise(self.note_list):
            if current_note.key == next_note.key:
                continue
            elif current_note.end > next_note.start:
                msg = _("Notes Overlapped")
                raise NotesOverlappedError(msg)
            if (diameter := current_note.portamento_right + next_note.portamento_left) and (
                next_note.start - current_note.end <= MAX_BREAK
            ):
                start = clamp(
                    current_note.end - current_note.portamento_right + next_note.portamento_offset,
                    current_note.start,
                    current_note.end,
                )
                end = clamp(
                    next_note.start + next_note.portamento_left + next_note.portamento_offset,
                    next_note.start,
                    next_note.end,
                )
                mid = clamp(
                    (current_note.end + next_note.start) / 2 + next_note.portamento_offset,
                    start,
                    end,
                )
                self.sigmoid_nodes.append(
                    SigmoidNode(
                        _start=start,
                        _end=end,
                        _center=mid,
                        _radius=diameter / 2,
                        _key_left=current_note.key,
                        _key_right=next_note.key,
                    )
                )
            else:
                mid = (current_note.end + next_note.start) / 2
                self.sigmoid_nodes.append(
                    SigmoidNode(
                        _start=mid - self.default_radius,
                        _end=mid + self.default_radius,
                        _center=mid,
                        _radius=self.default_radius,
                        _key_left=current_note.key,
                        _key_right=next_note.key,
                    )
                )

    def pitch_at_secs(self, secs: float) -> float:
        query = [node for node in self.sigmoid_nodes if node.start <= secs < node.end]
        if not query:
            on_note_index = find_index(self.note_list, lambda note: note.start <= secs < note.end)
            if on_note_index >= 0:
                return self.note_list[on_note_index].key * 100
            return (
                min(
                    self.note_list,
                    key=lambda note: min(abs(note.start - secs), abs(secs - note.end)),
                ).key
                * 100
            )
        elif len(query) == 1:
            return query[0].value_at_secs(secs)
        elif len(query) <= 3:
            first = query[0]
            last = query[-1]
            width = first.end - last.start
            bottom = first.value_at_secs(last.start)
            top = last.value_at_secs(first.end)
            diff1 = first.slope_at_secs(last.start)
            diff2 = last.slope_at_secs(first.end)
            return self.cubic_bezier(width, bottom, top, diff1, diff2)(secs - last.start)
        else:
            msg = "More than three sigmoid nodes overlapped"
            raise ParamsError(msg)

    @staticmethod
    def cubic_bezier(
        width: float, bottom: float, top: float, diff1: float, diff2: float
    ) -> Callable[[float], float]:
        a = (2 * (bottom - top) + (diff1 + diff2) * width) / width**3
        b = (3 * (top - bottom) - 2 * diff1 * width - diff2 * width) / width**2
        c = diff1
        d = bottom
        return lambda x: a * x**3 + b * x**2 + c * x + d


@dataclasses.dataclass
class GaussianNode:
    start: float = dataclasses.field(init=False)
    end: float = dataclasses.field(init=False)
    origin: float = dataclasses.field(init=False)
    gaussian_l: Callable[[float], float] = dataclasses.field(init=False)
    gaussian_r: Callable[[float], float] = dataclasses.field(init=False)
    is_end_point: dataclasses.InitVar[bool]
    _origin: dataclasses.InitVar[float]
    _depth: dataclasses.InitVar[float]
    _width: dataclasses.InitVar[float]
    _length_l: dataclasses.InitVar[float]
    _length_r: dataclasses.InitVar[float]
    ratio_miu: float = 0.447684
    ratio_sigma: float = 0.415
    expand: float = 2.5

    def __post_init__(
        self,
        is_end_point: bool,
        _origin: float,
        _depth: float,
        _width: float,
        _length_l: float,
        _length_r: float,
    ) -> None:
        self.origin = _origin
        _depth *= 100
        sigma_base = abs(self.ratio_sigma * _width)
        if is_end_point:
            sigma_l = min(sigma_base, _length_l / self.expand)
            self.start = self.origin - sigma_l * self.expand
            self.gaussian_l = lambda x: _depth * math.exp(-(((x - self.origin) / sigma_l) ** 2))
            sigma_r = min(sigma_base, _length_r / self.expand)
            self.end = self.origin + sigma_r * self.expand
            self.gaussian_r = lambda x: _depth * math.exp(-(((x - self.origin) / sigma_r) ** 2))
        else:
            sign = 1 if _depth > 0 else -1 if _depth < 0 else 0
            depth = abs(_depth)
            miu_base = self.ratio_miu * _width
            r2 = sigma_base**2

            length_base_l = self.expand * sigma_base - miu_base
            if _length_l >= length_base_l:
                self.start = self.origin - length_base_l
                self.gaussian_l = (
                    lambda x: sign
                    * depth
                    * math.exp(-(((x - self.origin - miu_base) / sigma_base) ** 2))
                )
            else:
                self.start = self.origin - _length_l
                k_l = _length_l / length_base_l
                miu_l = miu_base * k_l
                sigma_2l = r2 * k_l
                depth_l = depth * math.exp(miu_l**2 / r2 * (k_l - 1))
                self.gaussian_l = (
                    lambda x: sign
                    * depth_l
                    * math.exp(-((x - self.origin - miu_l) ** 2) / sigma_2l)
                )

            length_base_r = self.expand * sigma_base + miu_base
            if _length_r >= length_base_r:
                self.end = self.origin + length_base_r
                self.gaussian_r = (
                    lambda x: sign
                    * depth
                    * math.exp(-(((x - self.origin - miu_base) / sigma_base) ** 2))
                )
            else:
                self.end = self.origin + _length_r
                k_r = _length_r / length_base_r
                miu_r = miu_base * k_r
                sigma_2r = r2 * k_r
                depth_r = depth * math.exp(miu_r**2 / r2 * (k_r - 1))
                self.gaussian_r = (
                    lambda x: sign
                    * depth_r
                    * math.exp(-((x - self.origin - miu_r) ** 2) / sigma_2r)
                )

    def value_at_secs(self, secs: float) -> float:
        return self.gaussian_l(secs) if secs < self.origin else self.gaussian_r(secs)


@dataclasses.dataclass
class GaussianLayerGenerator:
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    gaussian_nodes: list[GaussianNode] = dataclasses.field(default_factory=list)

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        if not _note_list:
            return
        current_note = _note_list[0]
        self.gaussian_nodes.append(
            GaussianNode(
                is_end_point=True,
                _origin=current_note.start,
                _depth=-current_note.depth_left,
                _width=current_note.portamento_left,
                _length_l=math.nan,
                _length_r=current_note.end - current_note.start,
            )
        )
        for current_note, next_note in more_itertools.pairwise(_note_list):
            if next_note.start - current_note.end >= MAX_BREAK:
                self.gaussian_nodes.append(
                    GaussianNode(
                        is_end_point=True,
                        _origin=current_note.end,
                        _depth=current_note.depth_right,
                        _width=current_note.portamento_left,
                        _length_l=current_note.end - current_note.start,
                        _length_r=math.nan,
                    )
                )
                self.gaussian_nodes.append(
                    GaussianNode(
                        is_end_point=True,
                        _origin=next_note.start,
                        _depth=-next_note.depth_left,
                        _width=next_note.portamento_left,
                        _length_l=math.nan,
                        _length_r=next_note.end - next_note.start,
                    )
                )
            else:
                middle = (current_note.end + next_note.start) / 2
                origin = clamp(
                    middle + current_note.portamento_offset,
                    current_note.start,
                    current_note.end,
                )

                depth_l = (
                    current_note.depth_right
                    if current_note.key >= next_note.key
                    else -current_note.depth_right
                )
                self.gaussian_nodes.append(
                    GaussianNode(
                        is_end_point=False,
                        _origin=origin,
                        _depth=depth_l,
                        _width=-current_note.portamento_right,
                        _length_l=origin - current_note.start,
                        _length_r=next_note.end - origin,
                    )
                )

                depth_r = (
                    -next_note.depth_left
                    if current_note.key >= next_note.key
                    else next_note.depth_left
                )
                self.gaussian_nodes.append(
                    GaussianNode(
                        is_end_point=False,
                        _origin=origin,
                        _depth=depth_r,
                        _width=next_note.portamento_left,
                        _length_l=origin - current_note.start,
                        _length_r=next_note.end - origin,
                    )
                )
        self.gaussian_nodes.append(
            GaussianNode(
                is_end_point=True,
                _origin=_note_list[-1].end,
                _depth=-_note_list[-1].depth_right,
                _width=_note_list[-1].portamento_left,
                _length_l=_note_list[-1].end - _note_list[-1].start,
                _length_r=math.nan,
            )
        )

    def pitch_diff_at_secs(self, secs: float) -> float:
        return sum(
            node.value_at_secs(secs)
            for node in self.gaussian_nodes
            if node.start <= secs < node.end
        )


@dataclasses.dataclass
class VibratoNode:
    start: float
    end: float
    fade_left: float
    fade_right: float
    amplitude: float
    frequency: float
    phase: float

    def value_at_secs(self, secs: float) -> float:
        if self.end - self.start >= self.fade_left + self.fade_left:
            if secs < self.start + self.fade_left:
                zoom = (secs - self.start) / self.fade_left
            elif secs > self.end - self.fade_right:
                zoom = (self.end - secs) / self.fade_right
            else:
                zoom = 1.0
        else:
            mid = (self.start * self.fade_right + self.end * self.fade_left) / (
                self.fade_left + self.fade_right
            )
            if secs < mid:
                zoom = (secs - self.start) / self.fade_left
            else:
                zoom = (self.end - secs) / self.fade_right
        return (
            self.amplitude
            * zoom
            * 100.0
            * math.sin(math.tau * self.frequency * (secs - self.start) + self.phase)
        )


@dataclasses.dataclass
class VibratoLayerGenerator:
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    vibrato_nodes: list[VibratoNode] = dataclasses.field(default_factory=list)

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        for i in range(len(_note_list)):
            start, end = _note_list[i].start, _note_list[i].end
            if end - start <= _note_list[i].vibrato_start:
                continue
            if i < len(_note_list) - 1 and _note_list[i + 1].start - end < MAX_BREAK:
                end += min(
                    _note_list[i + 1].portamento_offset,
                    min(
                        _note_list[i + 1].vibrato_start,
                        _note_list[i + 1].end - _note_list[i + 1].start,
                    ),
                )
            if start >= end:
                continue
            self.vibrato_nodes.append(
                VibratoNode(
                    start=start + _note_list[i].vibrato_start,
                    end=end,
                    fade_left=_note_list[i].vibrato_left,
                    fade_right=_note_list[i].vibrato_right,
                    amplitude=_note_list[i].vibrato_depth / 2,
                    frequency=_note_list[i].vibrato_frequency,
                    phase=_note_list[i].vibrato_phase,
                )
            )

    def pitch_diff_at_secs(self, secs: float) -> float:
        return sum(
            node.value_at_secs(secs) for node in self.vibrato_nodes if node.start <= secs < node.end
        )
