from __future__ import annotations

import math
import statistics
from enum import Enum
from itertools import chain
from typing import Annotated, Callable, Literal, NamedTuple, Optional, Union

from more_itertools import chunked
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
from libresvip.model.point import PointList, linear_interpolation

from .ace_curve_utils import interpolate_akima
from .singers import DEFAULT_SEED, DEFAULT_SINGER, DEFAULT_SINGER_ID


class AcepAnchorPoint(NamedTuple):
    pos: float
    value: float


class AcepAnchorPoints(PointList, RootModel[list[AcepAnchorPoint]]):
    root: list[AcepAnchorPoint] = Field(default_factory=list)


class AcepParamCurve(BaseModel):
    curve_type: str = Field("data", alias="type")
    offset: int = 0
    values: list[float] = Field(default_factory=list)
    points: Optional[AcepAnchorPoints] = None
    points_vuv: Optional[list[float]] = Field(None, alias="pointsVUV")

    @field_validator("points", mode="before")
    @classmethod
    def validate_points(
        cls, points: list[float], _info: ValidationInfo
    ) -> AcepAnchorPoints:
        return AcepAnchorPoints(
            root=[AcepAnchorPoint(*each) for each in chunked(points or [], 2)]
        )

    @field_serializer("points", when_used="json-unless-none")
    def serialize_points(
        self, points: AcepAnchorPoints, _info: FieldSerializationInfo
    ) -> list[float]:
        return list(chain.from_iterable(points.root))

    def points2values(self) -> None:
        if self.curve_type == "anchor":
            if len(self.points.root) > 2:
                self.offset = math.floor(self.points.root[0].pos)
                self.values = interpolate_akima(
                    [point.pos for point in self.points.root],
                    [point.value for point in self.points.root],
                    list(range(self.offset, math.ceil(self.points.root[-1].pos) + 1)),
                )
            elif len(self.points.root) == 2:
                self.offset = math.floor(self.points.root[0].pos)
                self.values = [
                    linear_interpolation(self.points.root[0], self.points.root[-1], pos)
                    for pos in range(
                        self.offset, math.ceil(self.points.root[-1].pos) + 1
                    )
                ]

    def transform(self, value_transform: Callable[[float], float]) -> AcepParamCurve:
        return self.model_copy(
            update={"values": [value_transform(each) for each in self.values]},
            deep=True,
        )


class AcepParamCurveList(RootModel[list[AcepParamCurve]]):
    root: list[AcepParamCurve] = Field(default_factory=list)

    def plus(
        self, others, default_value: float, transform: Callable[[float], float]
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
            for self_curve in (
                curve for curve in self.root if start <= curve.offset < end
            ):
                index = self_curve.offset - start
                for value in self_curve.values:
                    result_curve.values[index] = value
                    index += 1
            for other_curve in (
                curve for curve in others.root if start <= curve.offset < end
            ):
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
            buffer = []
            pos = curve.offset
            for value in curve.values:
                pos += 1
                if predicate(value):
                    if buffer:
                        result.root.append(
                            AcepParamCurve(offset=pos - len(buffer), values=buffer)
                        )
                        buffer = []
                else:
                    buffer.append(value)

            if buffer:
                result.root.append(
                    AcepParamCurve(offset=pos - len(buffer), values=buffer)
                )

        return result

    def z_score_normalize(self, d: float = 1, b: float = 0) -> AcepParamCurveList:
        if not self.root:
            return self
        points = sum(curve.values for curve in self.root)
        miu = statistics.mean(points)
        sigma = statistics.stdev(points)
        return type(self)(
            root=[
                curve.transform(lambda x: (x - miu) / sigma * d + b)
                for curve in self.root
            ]
        )

    def minmax_normalize(self, r: float = 1, b: float = 0) -> AcepParamCurveList:
        if not self.root:
            return self
        minmax = sum((curve.values for curve in self.root), [])
        min_ = min(minmax)
        max_ = max(minmax)
        return type(self)(
            root=[
                curve.transform(lambda x: r * (2 * (x - min_) / (max_ - min_) - 1) + b)
                for curve in self.root
            ]
            if abs(max_ - min_) > 1e-3
            else [curve.transform(lambda x: 0) for curve in self.root]
        )


class AcepLyricsLanguage(Enum):
    CHINESE: Annotated[
        str,
        Field(
            title="Chinese",
        ),
    ] = "CHN"
    JAPANESE: Annotated[
        str,
        Field(
            title="Japanese",
        ),
    ] = "JPN"
    ENGLISH: Annotated[
        str,
        Field(
            title="English",
        ),
    ] = "ENG"


class AcepDebug(BaseModel):
    os: str = "windows"
    platform: str = "pc"
    version: str = "10"


class AcepMaster(BaseModel):
    gain: float = Field(default=0.0, le=6.0)


class AcepTempo(BaseModel):
    bpm: float = 0.0
    position: int = 0
    is_lerp: Optional[bool] = Field(False, alias="isLerp")


class AcepParams(BaseModel):
    pitch_delta: AcepParamCurveList = Field(
        default_factory=AcepParamCurveList, alias="pitchDelta"
    )
    energy: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    breathiness: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    tension: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    falsetto: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    gender: AcepParamCurveList = Field(default_factory=AcepParamCurveList)
    real_energy: AcepParamCurveList = Field(
        default_factory=AcepParamCurveList, alias="realEnergy"
    )
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
    phase: Optional[float] = 0.0
    start_pos: Optional[float] = Field(0.0, alias="startPos")
    release_level: Optional[float] = Field(0, alias="releaseLevel")
    release_ratio: Optional[float] = Field(0.0, alias="releaseRatio")
    attack_level: Optional[float] = Field(0, alias="attackLevel")
    attack_ratio: Optional[float] = Field(0.0, alias="attackRatio")


class AcepNote(BaseModel):
    pos: int = 0
    dur: int = 0
    pitch: int = 0
    language: AcepLyricsLanguage = AcepLyricsLanguage.CHINESE
    lyric: str = ""
    pronunciation: str = ""
    new_line: bool = Field(False, alias="newLine")
    consonant_len: Optional[int] = Field(None, alias="consonantLen")
    head_consonants: Optional[list[int]] = Field(
        default_factory=list, alias="headConsonants"
    )
    tail_consonants: Optional[list[int]] = Field(
        default_factory=list, alias="tailConsonants"
    )
    syllable: Optional[str] = ""
    br_len: int = Field(0, alias="brLen")
    vibrato: Optional[AcepVibrato] = None


class AcepPattern(BaseModel):
    name: str = ""
    pos: int = 0
    dur: int = 0
    clip_pos: int = Field(0, alias="clipPos")
    clip_dur: int = Field(0, alias="clipDur")
    enabled: Optional[bool] = True


class AcepAnalysedBeat(BaseModel):
    beat_times: list[float] = Field(default_factory=list, alias="beatTimes")
    length: float = 0
    offset: int = 0
    scales: list[int] = Field(default_factory=list)


class AcepAudioPattern(AcepPattern):
    path: str = ""
    gain: Optional[float] = None
    analysed_beat: Optional[AcepAnalysedBeat] = Field(None, alias="analysedBeat")


class AcepVocalPattern(AcepPattern):
    language: AcepLyricsLanguage = AcepLyricsLanguage.CHINESE
    extend_lyrics: str = Field("", alias="extendLyrics")
    notes: list[AcepNote] = Field(default_factory=list)
    parameters: AcepParams = Field(default_factory=AcepParams)


class AcepEmptyTrack(BaseModel):
    type_: Literal["empty"] = Field(default="empty", alias="type")
    name: str = ""
    color: str = "#91bcdc"
    gain: float = Field(0.0, le=6.0)
    pan: float = Field(0.0, le=10.0, ge=-10.0)
    mute: bool = False
    solo: bool = False
    record: bool = False
    channel: Optional[int] = 0
    listen: Optional[bool] = False

    def __len__(self):
        if not len(self.patterns):
            return 0
        last_pattern = self.patterns[-1]
        return last_pattern.pos + last_pattern.clip_dur - last_pattern.clip_pos


class AcepAudioTrack(AcepEmptyTrack):
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


class AcepVocalTrack(AcepEmptyTrack):
    type_: Literal["sing"] = Field(default="sing", alias="type")
    singer: AcepCustomSinger = Field(default_factory=AcepCustomSinger)
    language: AcepLyricsLanguage = AcepLyricsLanguage.CHINESE
    patterns: list[AcepVocalPattern] = Field(default_factory=list)


AcepTrack = Annotated[
    Union[AcepAudioTrack, AcepEmptyTrack, AcepVocalTrack], Field(discriminator="type_")
]


class AcepProject(BaseModel):
    beats_per_bar: int = Field(4, alias="beatsPerBar")
    color_index: int = Field(0, alias="colorIndex")
    duration: int = 0
    master: AcepMaster = Field(default_factory=AcepMaster)
    piano_cells: int = Field(2147483646, alias="pianoCells")
    tempos: list[AcepTempo] = Field(default_factory=list)
    track_cells: int = Field(2147483646, alias="trackCells")
    tracks: list[AcepTrack] = Field(default_factory=list)
    loop: Optional[bool] = False
    loop_start: Optional[int] = Field(0, alias="loopStart")
    loop_end: Optional[int] = Field(7680, alias="loopEnd")
    version: int = 5
    merged_pattern_index: int = Field(0, alias="mergedPatternIndex")
    record_pattern_index: int = Field(0, alias="recordPatternIndex")
    singer_library_id: Optional[str] = "1200593006"
    track_control_panel_w: Optional[int] = Field(0, alias="trackControlPanelW")
