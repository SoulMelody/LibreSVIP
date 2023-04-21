import abc
import inspect
import sys
from types import SimpleNamespace
from typing import (
    Annotated,
    Any,
    List,
    Literal,
    Optional,
    Protocol,
    Union,
    runtime_checkable,
)

from pydantic import BaseModel as PydanticBaseModel  # , Extra
from pydantic import Field, model_serializer, validator
from typing_extensions import Self

from libresvip.model.point import Point, PointList

try:
    import ujson as json
except ImportError:
    import json


json_loads = json.loads
json_dumps = json.dumps


class BaseModel(PydanticBaseModel):
    def __setattr__(self, name: str, value: Any) -> None:
        """
        To be able to use properties with setters
        """
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            setters = inspect.getmembers(
                self.__class__,
                predicate=lambda x: isinstance(x, property) and x.fset is not None,
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise e

    # class Config:
    #     json_loads = json.loads
    #     json_dumps = json.dumps
    #     # Uncomment the following line to enable strict mode
    #     # extra = Extra.forbid


@runtime_checkable
class BaseComplexModel(Protocol):
    @classmethod
    @abc.abstractmethod
    def default_repr(cls) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def from_str(cls, string: str) -> Self:
        pass


class Points(PointList[Point]):
    pass


class SongTempo(BaseModel):
    position: int = Field(default=0, alias="Position")
    bpm: float = Field(default=120.0, alias="BPM")


class TimeSignature(BaseModel):
    bar_index: int = Field(default=0, alias="BarIndex")
    numerator: int = Field(default=4, alias="Numerator")
    denominator: int = Field(default=4, alias="Denominator")


class ParamCurve(BaseModel):
    points: Points = Field(default_factory=Points, alias="PointList")

    @validator("points", pre=True)
    def load_points(cls, points) -> Points:  # noqa: N805
        return (
            points
            if isinstance(points, Points)
            else Points(root=[Point(*each) for each in points])
        )

    @model_serializer(mode='wrap')
    def _serialize(self, handler, info):
        data = handler(self)
        if info.mode == 'json':
            data["TotalPointsCount"] = len(self.points)
        return data

    def reduce_sample_rate(self, interval: int, interrupt_value: int = 0) -> Self:
        if interval <= 0:
            return self
        points = self.points
        if len(points) <= 1:
            return self
        result = []
        x_sum = 0
        y_sum = 0
        merged_count = 0
        prev_point = points[0]
        i = 0
        prev_point_added = False
        while i < len(points) - 1:
            i += 1
            prev_point_added = False
            current_point = points[i]
            if current_point[1] == interrupt_value:
                result.append(prev_point)
                prev_point = current_point
                continue
            elif prev_point[1] == interrupt_value:
                result.extend((prev_point, current_point))
                i += 1
                if i < len(points):
                    prev_point = points[i]
                prev_point_added = True
                continue
            pos = prev_point[0]
            first_loop = True
            while first_loop or (
                i < len(points)
                and points[i].x < pos + interval
                and points[i].y != interrupt_value
            ):
                if first_loop:
                    first_loop = False
                current_point = points[i]
                x_sum += prev_point.x
                y_sum += prev_point.y
                merged_count += 1
                prev_point = current_point
                i += 1
            result.append(
                Point(round(x_sum / merged_count), round(y_sum / merged_count))
            )
            x_sum = 0
            y_sum = 0
            merged_count = 0
            if i >= len(points):
                break
            i -= 1
        if not prev_point_added:
            result.append(prev_point)
        self.points = Points(root=result)
        return self

    def split_into_segments(self, interrupt_value: int = 0) -> List[List[Point]]:
        segments = []
        if len(self.points) == 0:
            return segments
        elif len(self.points) == 1:
            point = self.points[0]
            if point.x >= 0 and point.y != interrupt_value:
                segments.append([point])
            return segments
        buffer = []
        if interrupt_value != 0:
            for point in self.points:
                if point.x >= 0 and point.y < sys.maxsize // 2:
                    if point.y != interrupt_value:
                        buffer.append(point)
                    elif len(buffer):
                        segments.append(buffer.copy())
                        buffer.clear()
        else:
            current_point = self.points[0]
            i = 1
            while i < len(self.points):
                next_point = self.points[i]
                if current_point.y != interrupt_value:
                    buffer.append(current_point)
                elif next_point.y != interrupt_value:
                    if current_point.x >= 0 and (
                        i <= 1 or self.points[i - 2].y != interrupt_value
                    ):
                        buffer.append(current_point)
                elif len(buffer):
                    segments.append(buffer.copy())
                    buffer.clear()
                current_point = next_point
                i += 1
            if current_point.x < sys.maxsize // 2 and (
                current_point.y != interrupt_value
                or i <= 1
                or self.points[i - 2].y != interrupt_value
            ):
                buffer.append(current_point)
        if len(buffer):
            segments.append(buffer.copy())
        return segments


class Params(BaseModel):
    pitch: ParamCurve = Field(default_factory=ParamCurve, alias="Pitch")
    volume: ParamCurve = Field(default_factory=ParamCurve, alias="Volume")
    breath: ParamCurve = Field(default_factory=ParamCurve, alias="Breath")
    gender: ParamCurve = Field(default_factory=ParamCurve, alias="Gender")
    strength: ParamCurve = Field(default_factory=ParamCurve, alias="Strength")


class VibratoParam(BaseModel):
    start_percent: float = Field(0.0, alias="StartPercent")
    end_percent: float = Field(0.0, alias="EndPercent")
    is_anti_phase: bool = Field(False, alias="IsAntiPhase")
    amplitude: ParamCurve = Field(default_factory=ParamCurve, alias="Amplitude")
    frequency: ParamCurve = Field(default_factory=ParamCurve, alias="Frequency")


class Phones(BaseModel):
    head_length_in_secs: float = Field(1.0, alias="HeadLengthInSecs")
    mid_ratio_over_tail: float = Field(-1.0, alias="MidRatioOverTail")


class Note(BaseModel):
    start_pos: int = Field(0, alias="StartPos")
    length: int = Field(0, alias="Length")
    key_number: int = Field(0, alias="KeyNumber")
    head_tag: Optional[str] = Field(None, alias="HeadTag")
    lyric: str = Field("", alias="Lyric")
    pronunciation: Optional[str] = Field(None, alias="Pronunciation")
    edited_phones: Optional[Phones] = Field(None, alias="EditedPhones")
    vibrato: Optional[VibratoParam] = Field(None, alias="Vibrato")

    @property
    def end_pos(self) -> int:
        return self.start_pos + self.length


class TrackMixin(abc.ABC, BaseModel):
    title: str = Field("", alias="Title")
    mute: bool = Field(False, alias="Mute")
    solo: bool = Field(False, alias="Solo")
    volume: float = Field(1.0, alias="Volume")
    pan: float = Field(0.0, alias="Pan")


TrackType = SimpleNamespace(
    SINGING="Singing",
    INSTRUMENTAL="Instrumental",
)


class SingingTrack(TrackMixin):
    type_: Literal["Singing"] = Field(default=TrackType.SINGING, alias="Type")
    ai_singer_name: str = Field(default="", alias="AISingerName")
    reverb_preset: str = Field(default="", alias="ReverbPreset")
    note_list: List[Note] = Field(default_factory=list, alias="NoteList")
    edited_params: Params = Field(default_factory=Params, alias="EditedParams")


class InstrumentalTrack(TrackMixin):
    type_: Literal["Instrumental"] = Field(default=TrackType.INSTRUMENTAL, alias="Type")
    audio_file_path: str = Field(default="", alias="AudioFilePath")
    offset: int = Field(default=0, alias="Offset")


Track = Annotated[Union[SingingTrack, InstrumentalTrack], Field(discriminator="type_")]


class Project(BaseModel):
    version: str = Field(default="", alias="Version")
    song_tempo_list: List[SongTempo] = Field(
        default_factory=list, alias="SongTempoList"
    )
    time_signature_list: List[TimeSignature] = Field(
        default_factory=list, alias="TimeSignatureList"
    )
    track_list: List[Track] = Field(default_factory=list, alias="TrackList")
