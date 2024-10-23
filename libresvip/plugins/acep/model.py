from __future__ import annotations

import itertools
import math
import statistics
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    NamedTuple,
    Optional,
    Union,
)

from more_itertools import batched, minmax
from pydantic import (
    Field,
    FieldSerializationInfo,
    RootModel,
    ValidationInfo,
    field_serializer,
    field_validator,
)

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import BaseModel
from libresvip.model.point import PointList
from libresvip.utils.audio import audio_path_validator
from libresvip.utils.music_math import linear_interpolation

from .ace_curve_utils import interpolate_hermite
from .enums import AcepLyricsLanguage
from .singers import DEFAULT_SEED, DEFAULT_SINGER, DEFAULT_SINGER_ID

if TYPE_CHECKING:
    from collections.abc import Callable


class AcepAnchorPoint(NamedTuple):
    pos: float
    value: float


class AcepAnchorPoints(PointList[AcepAnchorPoint], RootModel[list[AcepAnchorPoint]]):
    root: list[AcepAnchorPoint] = Field(default_factory=list)


class AcepParamCurve(BaseModel):
    curve_type: str = Field("data", alias="type")
    offset: int = 0
    values: list[float] = Field(default_factory=list)
    points: Optional[AcepAnchorPoints] = None
    points_vuv: Optional[list[float]] = Field(None, alias="pointsVUV")

    @field_validator("points", mode="before")
    @classmethod
    def validate_points(cls, points: list[float], _info: ValidationInfo) -> AcepAnchorPoints:
        return AcepAnchorPoints(
            root=[AcepAnchorPoint._make(each) for each in batched(points or [], 2)]
        )

    @field_serializer("points", when_used="json-unless-none")
    def serialize_points(
        self, points: AcepAnchorPoints, _info: FieldSerializationInfo
    ) -> list[float]:
        return list(chain.from_iterable(points.root))

    def points2values(self) -> None:
        if self.curve_type == "anchor" and self.points is not None:
            if len(self.points.root) > 2:
                self.offset = math.floor(self.points.root[0].pos)
                self.values = interpolate_hermite(
                    [point.pos for point in self.points.root],
                    [point.value for point in self.points.root],
                    list(
                        range(
                            self.offset,
                            math.ceil(self.points.root[-1].pos) + 1,
                        )
                    ),
                )
            elif len(self.points.root) == 2:
                self.offset = math.floor(self.points.root[0].pos)
                self.values = [
                    linear_interpolation(pos, self.points.root[0], self.points.root[-1])
                    for pos in range(self.offset, math.ceil(self.points.root[-1].pos) + 1)
                ]

    def transform(self, value_transform: Callable[[float], float]) -> AcepParamCurve:
        return self.model_copy(
            update={"values": [value_transform(each) for each in self.values]},
            deep=True,
        )


class AcepParamCurveList(RootModel[list[AcepParamCurve]]):
    root: list[AcepParamCurve] = Field(default_factory=list)

    def plus(
        self,
        others: Optional[AcepParamCurveList],
        default_value: float,
        transform: Callable[[float], float],
    ) -> AcepParamCurveList:
        if not others:
            return self
        result_ranges = RangeInterval(
            [
                (curve.offset, curve.offset + len(curve.values))
                for curve in (self.root + others.root)
            ],
        ).sub_ranges()
        result_curve_list = type(self)()
        for start, end in result_ranges:
            result_curve = AcepParamCurve()
            result_curve.offset = start
            result_curve.values = [0.0] * (end - start)
            for self_curve in (curve for curve in self.root if start <= curve.offset < end):
                index = self_curve.offset - start
                for value in self_curve.values:
                    result_curve.values[index] = value
                    index += 1
            for other_curve in (curve for curve in others.root if start <= curve.offset < end):
                index = other_curve.offset - start
                for value in other_curve.values:
                    if result_curve.values[index] == 0.0:
                        result_curve.values[index] = default_value
                    result_curve.values[index] += transform(value)
                    index += 1
            result_curve_list.root.append(result_curve)
        return result_curve_list

    def exclude(self, predicate: Callable[[float], bool]) -> AcepParamCurveList:
        result = type(self)()
        for curve in self.root:
            buffer: list[float] = []
            pos = curve.offset
            for value in curve.values:
                pos += 1
                if predicate(value):
                    if buffer:
                        result.root.append(AcepParamCurve(offset=pos - len(buffer), values=buffer))
                        buffer.clear()
                else:
                    buffer.append(value)

            if buffer:
                result.root.append(AcepParamCurve(offset=pos - len(buffer), values=buffer))

        return result

    def z_score_normalize(self, d: float = 1, b: float = 0) -> AcepParamCurveList:
        if not self.root:
            return self
        points = [*itertools.chain.from_iterable(curve.values for curve in self.root)]
        miu = statistics.mean(points)
        sigma = statistics.stdev(points)
        return type(self)(
            root=[curve.transform(lambda x: (x - miu) / sigma * d + b) for curve in self.root]
        )

    def minmax_normalize(self, r: float = 1, b: float = 0) -> AcepParamCurveList:
        if not self.root:
            return self
        min_, max_ = minmax(
            itertools.chain.from_iterable(curve.values for curve in self.root),
            default=(0, 0),
        )
        return type(self)(
            root=[
                curve.transform(lambda x: r * (2 * (x - min_) / (max_ - min_) - 1) + b)
                for curve in self.root
            ]
            if abs(max_ - min_) > 1e-3
            else [curve.transform(lambda x: 0) for curve in self.root]
        )


class AcepMaster(BaseModel):
    gain: float = Field(default=0.0, le=6.0)


class AcepTempo(BaseModel):
    bpm: float = 0.0
    position: int = 0
    is_lerp: Optional[bool] = Field(False, alias="isLerp")


class AcepParams(BaseModel):
    pitch_delta: AcepParamCurveList = Field(default_factory=AcepParamCurveList, alias="pitchDelta")
    energy: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    breathiness: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    tension: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    falsetto: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    gender: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    real_energy: AcepParamCurveList = Field(default_factory=AcepParamCurveList, alias="realEnergy")
    real_breathiness: AcepParamCurveList = Field(
        default_factory=AcepParamCurveList, alias="realBreathiness"
    )
    real_tension: AcepParamCurveList = Field(
        default_factory=AcepParamCurveList, alias="realTension"
    )
    real_falsetto: AcepParamCurveList = Field(
        default_factory=AcepParamCurveList, alias="realFalsetto"
    )
    vuv: Optional[AcepParamCurveList] = Field(default_factory=AcepParamCurveList)


class AcepVibrato(BaseModel):
    start: float = 0.0
    amplitude: float = 0.0
    frequency: float = 0.0
    attack_len: float = Field(0.0, alias="attackLen")
    release_len: float = Field(0.0, alias="releaseLen")
    release_vol: float = Field(0.0, alias="releaseVol")
    phase: float = 0.0
    start_pos: float = Field(0.0, alias="startPos")
    release_level: float = Field(0.0, alias="releaseLevel")
    release_ratio: float = Field(0.0, alias="releaseRatio")
    attack_level: float = Field(0.0, alias="attackLevel")
    attack_ratio: float = Field(0.0, alias="attackRatio")


class AcepNote(BaseModel):
    pos: int = 0
    dur: int = 0
    pitch: int = 0
    language: AcepLyricsLanguage = AcepLyricsLanguage.CHINESE
    lyric: str = ""
    pronunciation: str = ""
    freezed_default_syllable: Optional[str] = Field(None, alias="freezedDefaultSyllable")
    new_line: bool = Field(False, alias="newLine")
    consonant_len: Optional[int] = Field(None, alias="consonantLen")
    head_consonants: Optional[list[float]] = Field(default_factory=list, alias="headConsonants")
    tail_consonants: Optional[list[float]] = Field(default_factory=list, alias="tailConsonants")
    syllable: Optional[str] = ""
    br_len: float = Field(0.0, alias="brLen")
    vibrato: Optional[AcepVibrato] = None
    extra_info: dict[str, Any] = Field(default_factory=dict, alias="extraInfo")


class AcepPattern(BaseModel):
    name: str = ""
    pos: float = 0.0
    dur: float = 0.0
    clip_pos: float = Field(0.0, alias="clipPos")
    clip_dur: float = Field(0.0, alias="clipDur")
    enabled: Optional[bool] = True
    color: Optional[str] = None
    extra_info: dict[str, Any] = Field(default_factory=dict, alias="extraInfo")


class AcepAnalysedBeat(BaseModel):
    beat_times: list[float] = Field(default_factory=list, alias="beatTimes")
    length: float = 0
    offset: int = 0
    scales: list[int] = Field(default_factory=list)


class AcepAudioFadeShape(BaseModel):
    offset_x: float = Field(0.0, alias="offsetX")
    offset_y: float = Field(0.0, alias="offsetY")


class AcepAudioFadeEffect(BaseModel):
    length: float = 0.0
    crossfade: Optional[bool] = False
    shape: AcepAudioFadeShape = Field(default_factory=AcepAudioFadeShape)


class AcepAudioPattern(AcepPattern):
    path: str = ""
    gain: Optional[float] = None
    analysed_beat: Optional[AcepAnalysedBeat] = Field(None, alias="analysedBeat")
    time_unit: Optional[str] = Field("sec", alias="timeUnit")
    fade_in: Optional[AcepAudioFadeEffect] = Field(None, alias="fadeIn")
    fade_out: Optional[AcepAudioFadeEffect] = Field(None, alias="fadeOut")
    validate_path = field_validator("path", mode="before")(audio_path_validator)


class AcepVocalPattern(AcepPattern):
    language: AcepLyricsLanguage = AcepLyricsLanguage.CHINESE
    extend_lyrics: str = Field("", alias="extendLyrics")
    notes: list[AcepNote] = Field(default_factory=list)
    time_unit: Optional[str] = Field("tick", alias="timeUnit")
    parameters: AcepParams = Field(default_factory=AcepParams)


class AcepTrackProperties(BaseModel):
    name: str = ""
    color: str = "#91bcdc"
    gain: float = Field(0.0, le=6.0)
    pan: float = Field(0.0, le=10.0, ge=-10.0)
    mute: bool = False
    solo: bool = False
    record: bool = False
    channel: Optional[int] = 0
    listen: Optional[bool] = False
    extra_info: dict[str, Any] = Field(default_factory=dict, alias="extraInfo")


class AcepEmptyTrack(AcepTrackProperties, BaseModel):
    type_: Literal["empty"] = Field(default="empty", alias="type")


class AcepAudioTrack(AcepTrackProperties, BaseModel):
    type_: Literal["audio"] = Field(default="audio", alias="type")
    patterns: list[AcepAudioPattern] = Field(default_factory=list)


class AcepSeedComposition(BaseModel):
    code: int = DEFAULT_SEED
    lock: bool = True
    style: float = 1.0
    timbre: float = 1.0


class AcepCustomSinger(BaseModel):
    composition: list[AcepSeedComposition] = Field(default_factory=list)
    state: str = "Unmixed"
    name: str = DEFAULT_SINGER
    singer_id: Optional[int] = Field(DEFAULT_SINGER_ID, alias="id")
    head: Optional[int] = -1
    router: Optional[int] = 1
    group: Optional[str] = ""


class AcepVocalTrack(AcepTrackProperties, BaseModel):
    type_: Literal["sing"] = Field(default="sing", alias="type")
    singer: AcepCustomSinger = Field(default_factory=AcepCustomSinger)
    language: AcepLyricsLanguage = AcepLyricsLanguage.CHINESE
    patterns: list[AcepVocalPattern] = Field(default_factory=list)

    def __len__(self) -> int:
        if not len(self.patterns):
            return 0
        last_pattern = self.patterns[-1]
        return int(last_pattern.pos + last_pattern.clip_dur - last_pattern.clip_pos)


class AcepChord(BaseModel):
    addeds: list[Literal["7", "j7", "b9", "9", "#9", "11", "#11", "b13", "13"]] = Field(
        default_factory=list
    )
    bass: int
    dur: int = 0
    root: int = -1
    type_: Literal["", "maj", "min", "dim", "sus2", "sus4", "aug"] = Field(default="", alias="type")


class AcepChordPattern(AcepPattern):
    chords: list[AcepChord] = Field(default_factory=list)
    time_unit: Optional[str] = Field("tick", alias="timeUnit")


class AcepChordTrack(AcepTrackProperties, BaseModel):
    type_: Literal["chord"] = Field(default="chord", alias="type")
    patterns: list[AcepChordPattern] = Field(default_factory=list)


AcepTrack = Annotated[
    Union[AcepAudioTrack, AcepEmptyTrack, AcepVocalTrack, AcepChordTrack],
    Field(discriminator="type_"),
]


class AcepTimeSignature(BaseModel):
    bar_pos: int = Field(0, alias="barPos")
    numerator: int = 4
    denominator: int = 4


class AcepProject(BaseModel):
    beats_per_bar: int = Field(4, alias="beatsPerBar")
    color_index: int = Field(0, alias="colorIndex")
    pattern_individual_color_index: Optional[int] = Field(0, alias="patternIndividualColorIndex")
    debug_info: dict[str, Any] = Field(default_factory=dict, alias="debugInfo")
    duration: int = 0
    extra_info: dict[str, Any] = Field(default_factory=dict, alias="extraInfo")
    master: AcepMaster = Field(default_factory=AcepMaster)
    piano_cells: int = Field(2147483646, alias="pianoCells")
    tempos: list[AcepTempo] = Field(default_factory=list)
    track_cells: int = Field(2147483646, alias="trackCells")
    tracks: list[AcepTrack] = Field(default_factory=list)
    loop: Optional[bool] = False
    loop_start: Optional[int] = Field(0, alias="loopStart")
    loop_end: Optional[int] = Field(7680, alias="loopEnd")
    version: int = 8
    version_revision: Optional[int] = Field(0, alias="versionRevision")
    merged_pattern_index: int = Field(0, alias="mergedPatternIndex")
    record_pattern_index: int = Field(0, alias="recordPatternIndex")
    singer_library_id: Optional[str] = "1200593006"
    time_signatures: list[AcepTimeSignature] = Field(default_factory=list, alias="timeSignatures")
    track_control_panel_w: Optional[int] = Field(0, alias="trackControlPanelW")
