from __future__ import annotations

import abc
import itertools
from types import SimpleNamespace
from typing import (
    Annotated,
    Literal,
    Protocol,
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
        # validate_assignment=True,
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
        points: Points | list[tuple[int, int]] | list[dict[str, int]],
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
        points = self.points.root
        if len(points) <= 1:
            return self
        result: list[Point] = []
        i = 0
        while i < len(points):
            point = points[i]
            if point.y == interrupt_value:
                result.append(point)
                i += 1
                continue
            run_start = i
            while i < len(points) and points[i].y != interrupt_value:
                i += 1
            run = points[run_start:i]
            if run_start > 0 and points[run_start - 1].y == interrupt_value:
                result.append(run[0])
                run = run[1:]
            if not run:
                continue
            if len(run) == 1:
                result.append(run[0])
                continue
            tail_point = run[-1]
            window_points = run[:-1]
            j = 0
            while j < len(window_points):
                bucket_start = window_points[j].x
                bucket = [window_points[j]]
                j += 1
                while j < len(window_points) and window_points[j].x < bucket_start + interval:
                    bucket.append(window_points[j])
                    j += 1
                result.append(
                    Point(
                        round(sum(point.x for point in bucket) / len(bucket)),
                        round(sum(point.y for point in bucket) / len(bucket)),
                    )
                )
            result.append(tail_point)
        return ParamCurve(points=Points(root=result))

    def split_into_segments(self, interrupt_value: int = 0) -> list[list[Point]]:
        end_point_x = Point.end_point().x
        segments: list[list[Point]] = []
        points = self.points.root
        if len(points) == 0:
            return segments
        elif len(points) == 1:
            point = points[0]
            if 0 <= point.x < end_point_x and point.y != interrupt_value:
                segments.append([point])
            return segments
        buffer: list[Point] = []
        if interrupt_value != 0:
            for point in points:
                if point.x >= 0 and point.y < end_point_x:
                    if point.y != interrupt_value:
                        buffer.append(point)
                    elif buffer:
                        segments.append(buffer.copy())
                        buffer.clear()
        else:
            for i, current_point in enumerate(points[:-1]):
                next_point = points[i + 1]
                if current_point.y != interrupt_value:
                    buffer.append(current_point)
                elif next_point.y != interrupt_value:
                    if current_point.x >= 0 and (i <= 0 or points[i - 1].y != interrupt_value):
                        buffer.append(current_point)
                elif buffer:
                    segments.append(buffer.copy())
                    buffer.clear()
            last_point = points[-1]
            if last_point.x < end_point_x and (
                last_point.y != interrupt_value or points[-2].y != interrupt_value
            ):
                buffer.append(last_point)
        if buffer:
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
    head_length_in_secs: float = Field(-1.0, alias="HeadLengthInSecs")
    mid_ratio_over_tail: float = Field(-1.0, alias="MidRatioOverTail")


class Note(BaseModel):
    start_pos: int = Field(0, alias="StartPos")
    length: int = Field(0, alias="Length")
    key_number: int = Field(0, alias="KeyNumber")
    head_tag: str | None = Field(None, alias="HeadTag")
    lyric: str = Field("", alias="Lyric")
    pronunciation: str | None = Field(None, alias="Pronunciation")
    edited_phones: Phones | None = Field(None, alias="EditedPhones")
    vibrato: VibratoParam | None = Field(None, alias="Vibrato")

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


Track = Annotated[SingingTrack | InstrumentalTrack, Field(discriminator="type_")]


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
        if len(projects) <= 1:
            msg = "No projects to merge"
            raise ValueError(msg)
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
        )

    def split_tracks(self, max_track_count: int) -> list[Project]:
        if not any(isinstance(track, SingingTrack) for track in self.track_list):
            msg = "No singing tracks found"
            raise ValueError(msg)
        return [
            self.model_copy(update={"track_list": track_chunk})
            for track_chunk in more_itertools.chunked(
                (track for track in self.track_list if isinstance(track, SingingTrack)),
                max_track_count,
            )
        ]
