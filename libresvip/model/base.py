from __future__ import annotations

import abc
import itertools
import sys
from types import SimpleNamespace
from typing import (
    Annotated,
    Literal,
    Optional,
    Protocol,
    Union,
    runtime_checkable,
)

import more_itertools
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    computed_field,
    field_validator,
)

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
from libresvip.model.point import Point, PointList


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        # # Uncomment the following lines to enable strict mode
        # extra="forbid",
        # strict=True,
    )


@runtime_checkable
class BaseComplexModel(Protocol):
    @classmethod
    @abc.abstractmethod
    def default_repr(cls) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def from_str(cls, string: str) -> BaseComplexModel:
        pass


class Points(PointList[Point], RootModel[list[Point]]):
    root: list[Point] = Field(default_factory=list)


class SongTempo(BaseModel):
    position: int = Field(default=0, alias="Position")
    bpm: float = Field(default=DEFAULT_BPM, alias="BPM")


class TimeSignature(BaseModel):
    bar_index: int = Field(default=0, alias="BarIndex")
    numerator: int = Field(default=4, alias="Numerator")
    denominator: int = Field(default=4, alias="Denominator")

    def bar_length(self, ticks_in_beat: int = TICKS_IN_BEAT) -> float:
        return (ticks_in_beat * 4) * self.numerator / self.denominator


class ParamCurve(BaseModel):
    points: Points = Field(default_factory=Points, alias="PointList")

    @field_validator("points", mode="before")
    @classmethod
    def load_points(
        cls,
        points: Union[Points, list[tuple[int, int]], list[dict[str, int]]],
        _info: ValidationInfo,
    ) -> Points:
        return (
            points if isinstance(points, Points) else Points(root=[Point(*each) for each in points])
        )

    @computed_field(alias="TotalPointsCount")
    def total_points_count(self) -> int:
        return len(self.points)

    def reduce_sample_rate(self, interval: int, interrupt_value: int = 0) -> ParamCurve:
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
                i < len(points) and points[i].x < pos + interval and points[i].y != interrupt_value
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
                Point(round(x_sum / merged_count), round(y_sum / merged_count)),
            )
            x_sum = 0
            y_sum = 0
            merged_count = 0
            if i >= len(points):
                break
            i -= 1
        if not prev_point_added:
            result.append(prev_point)
        return ParamCurve(points=Points(root=result))

    def split_into_segments(self, interrupt_value: int = 0) -> list[list[Point]]:
        segments: list[list[Point]] = []
        if len(self.points) == 0:
            return segments
        elif len(self.points) == 1:
            point = self.points[0]
            if point.x >= 0 and point.y != interrupt_value:
                segments.append([point])
            return segments
        buffer: list[Point] = []
        if interrupt_value != 0:
            for point in self.points.root:
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
                    if current_point.x >= 0 and (i <= 1 or self.points[i - 2].y != interrupt_value):
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
    note_list: list[Note] = Field(default_factory=list, alias="NoteList")
    edited_params: Params = Field(default_factory=Params, alias="EditedParams")


class InstrumentalTrack(TrackMixin):
    type_: Literal["Instrumental"] = Field(default=TrackType.INSTRUMENTAL, alias="Type")
    audio_file_path: str = Field(default="", alias="AudioFilePath")
    offset: int = Field(default=0, alias="Offset")


Track = Annotated[Union[SingingTrack, InstrumentalTrack], Field(discriminator="type_")]


class Project(BaseModel):
    version: str = Field(default="", alias="Version")
    song_tempo_list: list[SongTempo] = Field(
        default_factory=list,
        alias="SongTempoList",
    )
    time_signature_list: list[TimeSignature] = Field(
        default_factory=list,
        alias="TimeSignatureList",
    )
    track_list: list[Track] = Field(default_factory=list, alias="TrackList")

    @classmethod
    def merge_projects(cls, projects: list[Project]) -> Project:
        assert len(projects) > 1, "No projects to merge"
        sample_project = projects[0]
        if not all(
            project.time_signature_list == sample_project.time_signature_list
            and project.song_tempo_list == sample_project.song_tempo_list
            for project in projects[1:]
        ):
            msg = "All projects must have the same time signatures and tempos"
            raise ValueError(msg)
        return sample_project.model_copy(
            update={
                "track_list": [
                    *itertools.chain.from_iterable(project.track_list for project in projects)
                ]
            },
            deep=True,
        )

    def split_tracks(self, max_track_count: int) -> list[Project]:
        assert any(
            isinstance(track, SingingTrack) for track in self.track_list
        ), "No singing tracks found"
        return [
            self.model_copy(update={"track_list": track_chunk}, deep=True)
            for track_chunk in more_itertools.chunked(
                (track for track in self.track_list if isinstance(track, SingingTrack)),
                max_track_count,
            )
        ]
