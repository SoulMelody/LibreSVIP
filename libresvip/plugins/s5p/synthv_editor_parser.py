import dataclasses
import math
import pathlib

import more_itertools

from libresvip.core.tick_counter import shift_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point
from libresvip.model.synthv_pitch import NoteStruct, SynthVPitchSimulator
from libresvip.utils.music_math import (
    db_to_float,
    linear_interpolation,
    ratio_to_db,
)

from .model import (
    S5pDbDefaults,
    S5pInstrumental,
    S5pMeterItem,
    S5pMixer,
    S5pNote,
    S5pParameters,
    S5pProject,
    S5pTempoItem,
    S5pTrack,
)
from .options import InputOptions

TICK_RATE = 1470000


@dataclasses.dataclass
class SynthVEditorParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    time_signatures: list[TimeSignature] = dataclasses.field(init=False)

    def parse_project(self, s5p_project: S5pProject) -> Project:
        self.time_signatures = self.parse_time_signatures(s5p_project.meter)
        self.first_bar_length = round(self.time_signatures[0].bar_length())
        tempo_list = self.parse_tempos(s5p_project.tempo)
        self.synchronizer = TimeSynchronizer(tempo_list)
        track_list = self.parse_singing_tracks(s5p_project.tracks)
        if self.options.import_instrumental_track and s5p_project.instrumental.filename:
            track_list.append(
                self.parse_instrumental_track(s5p_project.instrumental, s5p_project.mixer)
            )
        return Project(
            time_signature_list=self.time_signatures,
            song_tempo_list=tempo_list,
            track_list=track_list,
        )

    @staticmethod
    def parse_time_signatures(
        meter: list[S5pMeterItem],
    ) -> list[TimeSignature]:
        time_signatures = [
            TimeSignature(
                bar_index=item.measure,
                numerator=item.beat_per_measure,
                denominator=item.beat_granularity,
            )
            for item in meter
        ]
        if not time_signatures:
            time_signatures.append(TimeSignature(bar_index=0, numerator=4, denominator=4))
        return time_signatures

    def parse_tempos(self, tempo: list[S5pTempoItem]) -> list[SongTempo]:
        return shift_tempo_list(
            [
                SongTempo(
                    position=item.position // TICK_RATE,
                    bpm=item.beat_per_minute,
                )
                for item in tempo
            ],
            self.first_bar_length,
        )

    def parse_singing_tracks(self, tracks: list[S5pTrack]) -> list[SingingTrack]:
        singing_tracks = []
        for i, track in enumerate(tracks, start=1):
            if note_list := self.parse_notes(track.notes, track.db_defaults):
                singing_tracks.append(
                    SingingTrack(
                        mute=track.mixer.muted,
                        solo=track.mixer.solo,
                        volume=self.parse_volume(track.mixer.gain_decibel),
                        pan=track.mixer.pan,
                        ai_singer_name=track.db_name or "",
                        title=track.name or f"Track {i}",
                        note_list=note_list,
                        edited_params=self.parse_params(
                            track.parameters,
                            [note for note in track.notes if note is not None],
                            track.db_defaults,
                        ),
                    )
                )
        return singing_tracks

    @staticmethod
    def parse_volume(gain: float) -> float:
        if gain >= 0:
            return min(gain / (ratio_to_db(4)) + 1.0, 2.0)
        else:
            return db_to_float(gain)

    def parse_instrumental_track(
        self, track: S5pInstrumental, mixer: S5pMixer
    ) -> InstrumentalTrack:
        return InstrumentalTrack(
            mute=mixer.instrumental_muted,
            volume=self.parse_volume(mixer.gain_instrumental_decibel),
            title=pathlib.Path(track.filename).name,
            audio_file_path=track.filename,
            offset=round(self.synchronizer.get_actual_ticks_from_secs(track.offset)),
        )

    def parse_notes(
        self, s5p_notes: list[S5pNote | None], db_defaults: S5pDbDefaults
    ) -> list[Note]:
        notes = []
        for s5p_note in s5p_notes:
            if s5p_note is None:
                continue
            note = Note(
                key_number=s5p_note.pitch,
                start_pos=round(s5p_note.onset / TICK_RATE),
                length=round(s5p_note.duration / TICK_RATE),
                lyric=s5p_note.lyric.lstrip(".").replace(" ", "") or db_defaults.lyric,
                pronunciation=s5p_note.comment
                if s5p_note.lyric.startswith(".") and s5p_note.comment
                else None,
            )
            notes.append(note)
        return notes

    def parse_params(
        self,
        parameters: S5pParameters,
        note_list: list[S5pNote],
        db_defaults: S5pDbDefaults,
    ) -> Params:
        params = Params()
        if self.options.import_pitch:
            note_structs = [self.note_to_note_struct(note, db_defaults) for note in note_list]
            pitch_simulator = SynthVPitchSimulator(
                synchronizer=self.synchronizer,
                _note_list=note_structs,
            )
            params.pitch = self.parse_pitch_curve(parameters, pitch_simulator, note_structs)
        return params

    def parse_pitch_curve(
        self,
        parameters: S5pParameters,
        pitch_simulator: SynthVPitchSimulator,
        note_structs: list[NoteStruct],
    ) -> ParamCurve:
        relative_point_groups = [
            [
                Point(
                    x=round(s5p_point.offset * (parameters.interval / TICK_RATE)),
                    y=round(s5p_point.value),
                )
                for s5p_point in point_group
            ]
            for point_group in more_itertools.split_when(
                parameters.pitch_delta.root, lambda p1, p2: p2.offset > p1.offset + 1
            )
            if len(point_group) > 1
        ]
        if not relative_point_groups:
            relative_point_groups = []
        points = [Point.start_point()]
        for start_secs, end_secs in self.iter_note_segments(note_structs):
            start_ticks = round(self.synchronizer.get_actual_ticks_from_secs(start_secs))
            end_ticks = round(self.synchronizer.get_actual_ticks_from_secs(end_secs))
            points.append(Point(start_ticks + self.first_bar_length, -100))
            points.extend(
                Point(
                    x=ticks + self.first_bar_length,
                    y=round(
                        pitch_simulator.pitch_at_ticks(ticks)
                        + self.relative_pitch_at_ticks(ticks, relative_point_groups)
                    ),
                )
                for ticks in range(start_ticks, end_ticks, 5)
            )
            points.append(
                Point(
                    x=end_ticks + self.first_bar_length,
                    y=round(
                        pitch_simulator.pitch_at_ticks(end_ticks)
                        + self.relative_pitch_at_ticks(end_ticks, relative_point_groups)
                    ),
                )
            )
            points.append(Point(end_ticks + self.first_bar_length, -100))
        points.append(Point.end_point())
        return ParamCurve(points=Points(root=points))

    @staticmethod
    def iter_note_segments(note_structs: list[NoteStruct]) -> list[tuple[float, float]]:
        if not note_structs:
            return []
        segments: list[tuple[float, float]] = []
        start_secs = note_structs[0].start
        end_secs = note_structs[0].end
        for note in note_structs[1:]:
            if note.start - end_secs > 0.01:
                segments.append((start_secs, end_secs))
                start_secs = note.start
            end_secs = note.end
        segments.append((start_secs, end_secs))
        return segments

    @staticmethod
    def relative_pitch_at_ticks(ticks: int, relative_point_groups: list[list[Point]]) -> float:
        for points in relative_point_groups:
            if not points:
                continue
            if ticks < points[0].x or ticks > points[-1].x:
                continue
            if len(points) == 1:
                return points[0].y
            if ticks <= points[0].x:
                return points[0].y
            if ticks >= points[-1].x:
                return points[-1].y
            for prev_point, point in more_itertools.pairwise(points):
                if prev_point.x <= ticks <= point.x:
                    return linear_interpolation(ticks, prev_point, point)
        return 0.0

    def note_to_note_struct(self, note: S5pNote, db_defaults: S5pDbDefaults) -> NoteStruct:
        onset = round(note.onset / TICK_RATE)
        end_pos = onset + round(note.duration / TICK_RATE)
        return NoteStruct(
            key=note.pitch,
            start=self.synchronizer.get_actual_secs_from_ticks(onset),
            end=self.synchronizer.get_actual_secs_from_ticks(end_pos),
            portamento_offset=note.t_f0_offset or 0.0,
            portamento_left=note.t_f0_left if note.t_f0_left is not None else db_defaults.t_f0_left,
            portamento_right=(
                note.t_f0_right if note.t_f0_right is not None else db_defaults.t_f0_right
            ),
            depth_left=note.d_f0_left if note.d_f0_left is not None else db_defaults.d_f0_left,
            depth_right=note.d_f0_right if note.d_f0_right is not None else db_defaults.d_f0_right,
            vibrato_start=(
                note.t_f0_vbr_start
                if note.t_f0_vbr_start is not None
                else db_defaults.t_f0_vbr_start
            ),
            vibrato_left=(
                note.t_f0_vbr_left if note.t_f0_vbr_left is not None else db_defaults.t_f0_vbr_left
            ),
            vibrato_right=(
                note.t_f0_vbr_right
                if note.t_f0_vbr_right is not None
                else db_defaults.t_f0_vbr_right
            ),
            vibrato_depth=(
                (note.d_f0_vbr if note.d_f0_vbr is not None else db_defaults.d_f0_vbr) * 40
            ),
            vibrato_frequency=(
                note.f_f0_vbr if note.f_f0_vbr is not None else db_defaults.f_f0_vbr
            ),
            vibrato_phase=math.pi
            * (note.p_f0_vbr if note.p_f0_vbr is not None else db_defaults.p_f0_vbr),
        )
