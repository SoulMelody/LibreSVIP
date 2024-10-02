import dataclasses
import math
import pathlib
from collections.abc import Callable

from libresvip.core.constants import DEFAULT_CHINESE_LYRIC
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point
from libresvip.utils.music_math import db_to_float

from .model import (
    VocalShifterLabel,
    VocalShifterNote,
    VocalShifterPatternData,
    VocalShifterPatternMetadata,
    VocalShifterPatternType,
    VocalShifterProjectData,
    VocalShifterProjectMetadata,
    VocalShifterTrackMetadata,
)
from .options import InputOptions
from .utils import ansi2unicode


@dataclasses.dataclass
class VocalShifterParser:
    options: InputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    tick_rate: float = dataclasses.field(init=False)

    def parse_project(self, vshp_proj: VocalShifterProjectData) -> Project:
        project = Project(
            song_tempo_list=self.parse_tempo(vshp_proj.project_metadata),
            time_signature_list=self.parse_time_signature(vshp_proj.project_metadata),
        )
        project.track_list = self.parse_track_list(vshp_proj)
        return project

    def parse_tempo(self, vshp_metadata: VocalShifterProjectMetadata) -> list[SongTempo]:
        tempo_list = [
            SongTempo(
                position=0,
                bpm=vshp_metadata.tempo,
            )
        ]
        self.synchronizer = TimeSynchronizer(tempo_list)
        self.tick_rate = vshp_metadata.tempo / 25
        return tempo_list

    def parse_time_signature(
        self, vshp_metadata: VocalShifterProjectMetadata
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=0,
                numerator=vshp_metadata.numerator,
                denominator=vshp_metadata.denominator,
            )
        ]

    def parse_track_list(self, vshp_proj: VocalShifterProjectData) -> list[Track]:
        track_list = []
        for pattern_metadata, pattern_data in zip(
            vshp_proj.pattern_metadatas, vshp_proj.pattern_datas
        ):
            if (
                pattern_data.header.pattern_type == VocalShifterPatternType.WAVE
                and not self.options.wave_to_singing
            ):
                track = self.parse_instrumental_track(
                    pattern_metadata,
                    pattern_data,
                    vshp_proj.track_metadatas[pattern_metadata.track_index],
                )
            else:
                track = self.parse_singing_track(
                    pattern_metadata,
                    pattern_data,
                    vshp_proj.track_metadatas[pattern_metadata.track_index],
                )
            track_list.append(track)
        return track_list

    def parse_instrumental_track(
        self,
        pattern_metadata: VocalShifterPatternMetadata,
        pattern_data: VocalShifterPatternData,
        track_metadata: VocalShifterTrackMetadata,
    ) -> InstrumentalTrack:
        sample_rate = pattern_data.header.sample_rate
        sample_offset = pattern_metadata.offset_samples + pattern_metadata.offset_correction
        offset_in_seconds = sample_offset / sample_rate
        offset_in_ticks = self.synchronizer.get_actual_ticks_from_secs(offset_in_seconds)
        return InstrumentalTrack(
            audio_file_path=ansi2unicode(pattern_metadata.path_and_ext.split(b"\x00")[0]),
            offset=offset_in_ticks,
            solo=track_metadata.solo,
            mute=track_metadata.mute,
            volume=track_metadata.volume,
            pan=track_metadata.pan,
        )

    def parse_singing_track(
        self,
        pattern_metadata: VocalShifterPatternMetadata,
        pattern_data: VocalShifterPatternData,
        track_metadata: VocalShifterTrackMetadata,
    ) -> SingingTrack:
        file_path = pathlib.Path(ansi2unicode(pattern_metadata.path_and_ext.split(b"\x00")[0]))
        track = SingingTrack(
            title=file_path.stem,
            solo=track_metadata.solo,
            mute=track_metadata.mute,
            volume=track_metadata.volume,
            pan=track_metadata.pan,
        )
        sample_offset = pattern_metadata.offset_samples + pattern_metadata.offset_correction
        offset_in_seconds = sample_offset / pattern_data.header.sample_rate
        offset_in_ticks = int(self.synchronizer.get_actual_ticks_from_secs(offset_in_seconds))
        track.note_list = self.parse_note_list(
            offset_in_ticks,
            pattern_data.notes.notes,
            pattern_data.labels.labels if pattern_data.labels else [],
        )
        track.edited_params = self.parse_params(offset_in_seconds, pattern_data)
        return track

    def parse_note_list(
        self,
        offset: int,
        notes: list[VocalShifterNote],
        labels: list[VocalShifterLabel],
    ) -> list[Note]:
        note_list = []
        if labels:
            for label in labels:
                target_note = next(
                    (
                        note
                        for note in notes
                        if note.start_tick <= label.start_tick <= note.start_tick + note.length
                    ),
                    None,
                )
                note_list.append(
                    Note(
                        start_pos=offset + round(label.start_tick * self.tick_rate),
                        length=int((label.end_tick - label.start_tick) * self.tick_rate),
                        key_number=target_note.pitch // 100 if target_note is not None else 60,
                        lyric=ansi2unicode(label.name.partition(b"\x00")[0]),
                    )
                )
        else:
            note_list.extend(
                Note(
                    start_pos=offset + round(note.start_tick * self.tick_rate),
                    length=int(note.length * self.tick_rate),
                    key_number=note.pitch // 100,
                    lyric=DEFAULT_CHINESE_LYRIC,
                )
                for note in notes
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
            pitch=self.parse_pitch_curve(offset, pattern_data),
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
                (10.0).__rfloordiv__,
            )
        if self.options.import_formant:
            params.gender = self.parse_param_curve(
                offset,
                pattern_data,
                "frm",
                (10.0).__rfloordiv__,
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
                    pitch_curve.points.append(
                        Point(
                            round(self.synchronizer.get_actual_ticks_from_secs(offset)) + 1920,
                            -100,
                        )
                    )
                    has_pitch = True
                pitch_curve.points.append(
                    Point(
                        round(self.synchronizer.get_actual_ticks_from_secs(offset)) + 1920,
                        value,
                    )
                )
            elif has_pitch:
                pitch_curve.points.append(
                    Point(
                        round(self.synchronizer.get_actual_ticks_from_secs(offset)) + 1920,
                        -100,
                    )
                )
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
                Point(
                    round(self.synchronizer.get_actual_ticks_from_secs(offset)) + 1920,
                    int(mapping_func(value)),
                )
            )
            offset += time_step
        return param_curve
