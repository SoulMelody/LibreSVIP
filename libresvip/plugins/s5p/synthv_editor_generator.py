import dataclasses
import math
import sys

import more_itertools

from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point
from libresvip.model.synthv_pitch import NoteStruct, SynthVPitchSimulator
from libresvip.utils.music_math import ratio_to_db

from .model import (
    S5pDbDefaults,
    S5pInstrumental,
    S5pMeterItem,
    S5pMixer,
    S5pNote,
    S5pParameters,
    S5pPoint,
    S5pPoints,
    S5pProject,
    S5pTempoItem,
    S5pTrack,
    S5pTrackMixer,
)
from .options import OutputOptions

TICK_RATE = 1470000


@dataclasses.dataclass
class SynthVEditorGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    time_signatures: list[TimeSignature] = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> S5pProject:
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        self.time_signatures = project.time_signature_list
        s5p_project = S5pProject(
            tempo=self.generate_tempos(project.song_tempo_list),
            meter=self.generate_time_signatures(project.time_signature_list),
            tracks=self.generate_singing_tracks(project.track_list),
        )
        if (
            instrumental_track_and_mixer := next(
                (
                    self.generate_instrumental_track_and_mixer(track)
                    for track in project.track_list
                    if isinstance(track, InstrumentalTrack)
                ),
                None,
            )
        ) is not None:
            s5p_project.instrumental, s5p_project.mixer = instrumental_track_and_mixer
        return s5p_project

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[S5pTempoItem]:
        song_tempo_list = skip_tempo_list(song_tempo_list, self.first_bar_length)
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return [
            S5pTempoItem(
                position=song_tempo.position * TICK_RATE,
                beat_per_minute=song_tempo.bpm,
            )
            for song_tempo in song_tempo_list
        ]

    @staticmethod
    def generate_time_signatures(
        time_signature_list: list[TimeSignature],
    ) -> list[S5pMeterItem]:
        return [
            S5pMeterItem(
                measure=time_signature.bar_index,
                beat_per_measure=time_signature.numerator,
                beat_granularity=time_signature.denominator,
            )
            for time_signature in time_signature_list
        ]

    @staticmethod
    def generate_volume(volume: float) -> float:
        return max(ratio_to_db(max(volume, 0.01)), -70) if volume > 0 else -70

    def generate_singing_tracks(self, track_list: list[Track]) -> list[S5pTrack]:
        tracks = []
        for i, track in enumerate(track_list):
            if isinstance(track, SingingTrack):
                s5p_notes = self.generate_notes(track.note_list)
                track_mixer = S5pTrackMixer(
                    solo=track.solo,
                    muted=track.mute,
                    pan=track.pan,
                    gain_decibel=self.generate_volume(track.volume),
                )

                s5p_track = S5pTrack(
                    display_order=i,
                    name=track.title,
                    db_name=track.ai_singer_name,
                    notes=s5p_notes,
                    mixer=track_mixer,
                )
                if track.edited_params is not None:
                    s5p_track.parameters = self.generate_parameters(
                        track.edited_params, s5p_notes, s5p_track.db_defaults
                    )
                tracks.append(s5p_track)
        if not tracks:
            tracks.append(
                S5pTrack(
                    name="Unnamed Track",
                    notes=[None],
                )
            )
        return tracks

    def generate_notes(self, note_list: list[Note]) -> list[S5pNote]:
        return [
            S5pNote(
                lyric=note.lyric,
                onset=note.start_pos * TICK_RATE,
                duration=note.length * TICK_RATE,
                pitch=note.key_number,
            )
            for note in note_list
        ]

    def generate_instrumental_track_and_mixer(
        self, track: InstrumentalTrack
    ) -> tuple[S5pInstrumental, S5pMixer]:
        return S5pInstrumental(
            filename=track.audio_file_path,
            offset=self.synchronizer.get_actual_secs_from_ticks(track.offset),
        ), S5pMixer(
            gain_instrumental_decibel=self.generate_volume(track.volume),
            instrumental_muted=track.mute,
        )

    def generate_parameters(
        self, edited_params: Params, note_list: list[S5pNote], db_defaults: S5pDbDefaults
    ) -> S5pParameters:
        interval = round(TICK_RATE * 3.75)
        pitch_simulator = SynthVPitchSimulator(
            synchronizer=self.synchronizer,
            _note_list=[self.note_to_note_struct(note, db_defaults) for note in note_list],
        )
        return S5pParameters(
            pitch_delta=self.generate_pitch_delta(
                edited_params.pitch.points.root,
                pitch_simulator,
                interval,
            ),
            interval=interval,
        )

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

    def generate_pitch_delta(
        self, pitch: list[Point], pitch_simulator: SynthVPitchSimulator, interval: int
    ) -> S5pPoints:
        relative_points = [
            S5pPoint(
                offset=round((point.x - self.first_bar_length) / (interval / TICK_RATE)),
                value=point.y - pitch_simulator.pitch_at_ticks(point.x - self.first_bar_length),
            )
            for point in pitch
            if point.y != -100 and self.first_bar_length <= point.x < sys.maxsize // 2
        ]
        return S5pPoints(root=self.compress_pitch_delta(relative_points))

    @staticmethod
    def compress_pitch_delta(relative_points: list[S5pPoint]) -> list[S5pPoint]:
        if not relative_points:
            return []
        compressed_points: list[S5pPoint] = []
        tolerance = 1e-3
        for point_group in more_itertools.split_when(
            relative_points, lambda p1, p2: p2.offset > p1.offset + 1
        ):
            group = list(point_group)
            if not group:
                continue
            nonzero_indexes = [
                index for index, point in enumerate(group) if abs(point.value) > tolerance
            ]
            if not nonzero_indexes:
                continue
            if len(group) == 1:
                compressed_points.extend((group[0], group[0]))
                continue
            start_index = max(0, nonzero_indexes[0] - 1)
            end_index = min(len(group) - 1, nonzero_indexes[-1] + 1)
            compressed_points.extend(group[start_index : end_index + 1])
        return compressed_points
