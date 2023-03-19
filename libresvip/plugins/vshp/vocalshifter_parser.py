import dataclasses
import math
import pathlib
from typing import Callable, Dict, List

from construct import Container
from pydub.utils import db_to_float

from libresvip.core.constants import DEFAULT_LYRIC
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Point,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .model import (
    VocalShifterPatternData,
    VocalShifterPatternMetadata,
    VocalShifterPatternType,
    VocalShifterProjectData,
    VocalShifterProjectMetadata,
)
from .options import InputOptions
from .utils import ansi2unicode


@dataclasses.dataclass
class VocalShifterParser:
    options: InputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    tick_rate: float = dataclasses.field(init=False)
    track_index2metadata: Dict[int, Container] = dataclasses.field(
        default_factory=dict
    )

    def parse_project(self, vshp_proj: VocalShifterProjectData) -> Project:
        project = Project(
            SongTempoList=self.parse_tempo(vshp_proj.project_metadata),
            TimeSignatureList=self.parse_time_signature(vshp_proj.project_metadata),
        )
        project.track_list = self.parse_track_list(vshp_proj)
        return project

    def parse_tempo(
        self, vshp_metadata: VocalShifterProjectMetadata
    ) -> List[SongTempo]:
        tempo_list = [
            SongTempo(
                Position=0,
                BPM=vshp_metadata.tempo,
            )
        ]
        self.synchronizer = TimeSynchronizer(tempo_list)
        self.tick_rate = vshp_metadata.tempo / 25
        return tempo_list

    def parse_time_signature(
        self, vshp_metadata: VocalShifterProjectMetadata
    ) -> List[TimeSignature]:
        time_signature_list = [
            TimeSignature(
                BarIndex=0,
                Numerator=vshp_metadata.numerator,
                Denominator=vshp_metadata.denominator,
            )
        ]
        return time_signature_list

    def parse_track_list(self, vshp_proj: VocalShifterProjectData) -> List[Track]:
        track_list = []
        for i, track_metadata in enumerate(vshp_proj.track_metadatas):
            self.track_index2metadata[i + 1] = track_metadata
        for pattern_metadata, pattern_data in zip(
            vshp_proj.pattern_metadatas, vshp_proj.pattern_datas
        ):
            if (
                pattern_data.header.pattern_type == VocalShifterPatternType.WAVE
                and not self.options.wave_to_singing
            ):
                track = self.parse_instrumental_track(pattern_metadata, pattern_data)
            else:
                track = self.parse_singing_track(pattern_metadata, pattern_data)
            track_list.append(track)
        return track_list

    def parse_instrumental_track(
        self,
        pattern_metadata: VocalShifterPatternMetadata,
        pattern_data: VocalShifterPatternData,
    ) -> InstrumentalTrack:
        sample_rate = pattern_data.header.sample_rate
        sample_offset = (
            pattern_metadata.offset_samples + pattern_metadata.offset_correction
        )
        offset_in_seconds = sample_offset / sample_rate
        offset_in_ticks = self.synchronizer.get_actual_ticks_from_secs(
            offset_in_seconds
        ) - 1920
        track_metadata = self.track_index2metadata[pattern_metadata.track_index]
        track = InstrumentalTrack(
            AudioFilePath=ansi2unicode(pattern_metadata.path_and_ext.split(b"\x00")[0]),
            Offset=offset_in_ticks,
            Solo=track_metadata.solo,
            Mute=track_metadata.mute,
            Volume=track_metadata.volume,
            Pan=track_metadata.pan,
        )
        return track

    def parse_singing_track(
        self,
        pattern_metadata: VocalShifterPatternMetadata,
        pattern_data: VocalShifterPatternData,
    ) -> SingingTrack:
        track_metadata = self.track_index2metadata[pattern_metadata.track_index]
        file_path = pathlib.Path(
            ansi2unicode(pattern_metadata.path_and_ext.split(b"\x00")[0])
        )
        track = SingingTrack(
            Title=file_path.stem,
            Solo=track_metadata.solo,
            Mute=track_metadata.mute,
            Volume=track_metadata.volume,
            Pan=track_metadata.pan,
        )
        sample_offset = (
            pattern_metadata.offset_samples + pattern_metadata.offset_correction
        )
        offset_in_seconds = sample_offset / pattern_data.header.sample_rate
        offset_in_ticks = self.synchronizer.get_actual_ticks_from_secs(
            offset_in_seconds
        ) - 1920
        track.note_list = self.parse_note_list(
            offset_in_ticks,
            pattern_data.notes.notes,
            pattern_data.labels.labels if pattern_data.labels else [],
        )
        track.edited_params = self.parse_params(offset_in_seconds, pattern_data)
        return track

    def parse_note_list(
        self, offset: int, notes: List[Container], labels: List[Container]
    ) -> List[Note]:
        note_list = []
        if labels and len(labels.labels) == len(notes):
            for note, label in zip(notes, labels):
                if label.start_tick != note.start_tick:
                    note_list.append(
                        Note(
                            StartPos=offset + round(note.start_tick * self.tick_rate),
                            Length=int(note.length * self.tick_rate),
                            KeyNumber=note.pitch // 100,
                            Lyric=DEFAULT_LYRIC,
                        )
                    )
                else:
                    note_list.append(
                        Note(
                            StartPos=offset + round(note.start_tick * self.tick_rate),
                            Length=int(note.length * self.tick_rate),
                            KeyNumber=note.pitch // 100,
                            Lyric=ansi2unicode(label.name.split(b"\x00")[0]),
                        )
                    )
        else:
            for note in notes:
                note_list.append(
                    Note(
                        StartPos=offset + round(note.start_tick * self.tick_rate),
                        Length=int(note.length * self.tick_rate),
                        KeyNumber=note.pitch // 100,
                        Lyric=DEFAULT_LYRIC,
                    )
                )
        return note_list

    @staticmethod
    def volume_to_value(volume: float) -> float:
        db = math.log(volume, 1 + 1 / 9)
        float_value = db_to_float(db)
        return round(1000 * float_value - 1000)

    def parse_params(
        self,
        offset: float,
        pattern_data: VocalShifterPatternData,
    ) -> Params:
        params = Params(
            Pitch=self.parse_pitch_curve(offset, pattern_data),
        )
        if self.options.import_dynamics:
            params.volume = self.parse_param_curve(
                offset,
                pattern_data,
                "dyn" if self.options.use_edited_dynamics else "ori_dyn",
                self.volume_to_value,
            )
        if self.options.import_breath:
            params.breath = self.parse_param_curve(
                offset,
                pattern_data,
                "bre",
                lambda x: x // 10,
            )
        if self.options.import_formant:
            params.gender = self.parse_param_curve(
                offset,
                pattern_data,
                "frm",
                lambda x: x // 10,
            )
        return params

    def parse_pitch_curve(
        self,
        offset: float,
        pattern_data: VocalShifterPatternData,
    ) -> ParamCurve:
        pitch_curve = ParamCurve()
        pitch_curve.points.append(Point.start_point())
        has_pitch = False
        time_step = 1 / pattern_data.header.points_per_second
        for point in pattern_data.points:
            value = point.pit if self.options.use_edited_pitch else point.ori_pit
            if value != 0:
                if not has_pitch:
                    pitch_curve.points.append(Point(self.synchronizer.get_actual_ticks_from_secs(offset), -100))
                    has_pitch = True
                pitch_curve.points.append(
                    Point(
                        self.synchronizer.get_actual_ticks_from_secs(offset),
                        value,
                    )
                )
            else:
                if has_pitch:
                    pitch_curve.points.append(Point(self.synchronizer.get_actual_ticks_from_secs(offset), -100))
                    has_pitch = False
            offset += time_step
        pitch_curve.points.append(Point.end_point())
        return pitch_curve

    def parse_param_curve(
        self,
        offset: float,
        pattern_data: VocalShifterPatternData,
        attr_name: str,
        mapping_func: Callable[[int], float],
    ) -> ParamCurve:
        param_curve = ParamCurve()
        time_step = 1 / pattern_data.header.points_per_second
        for point in pattern_data.points:
            value = getattr(point, attr_name)
            param_curve.points.append(
                Point(self.synchronizer.get_actual_ticks_from_secs(offset), mapping_func(value))
            )
            offset += time_step
        return param_curve
