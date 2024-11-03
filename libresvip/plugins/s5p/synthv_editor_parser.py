import dataclasses
import functools
import math
import operator
import pathlib
from typing import Optional, cast

import more_itertools
import portion
import sortedcontainers

from libresvip.core.tick_counter import shift_tempo_list
from libresvip.core.time_interval import PiecewiseIntervalDict
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
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
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
    S5pPoints,
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
    vibrato_value_interval_dict: PiecewiseIntervalDict = dataclasses.field(init=False)
    vibrato_coef_interval_dict: PiecewiseIntervalDict = dataclasses.field(init=False)

    def parse_project(self, s5p_project: S5pProject) -> Project:
        time_signature_list = self.parse_time_signatures(s5p_project.meter)
        self.first_bar_length = round(time_signature_list[0].bar_length())
        tempo_list = self.parse_tempos(s5p_project.tempo)
        self.synchronizer = TimeSynchronizer(tempo_list)
        track_list = self.parse_singing_tracks(s5p_project.tracks)
        if self.options.import_instrumental_track and s5p_project.instrumental.filename:
            track_list.append(
                self.parse_instrumental_track(s5p_project.instrumental, s5p_project.mixer)
            )
        return Project(
            time_signature_list=time_signature_list,
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
        if not len(time_signatures):
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

    def parse_singing_tracks(self, tracks: list[S5pTrack]) -> list[Track]:
        return [
            SingingTrack(
                mute=track.mixer.muted,
                solo=track.mixer.solo,
                volume=self.parse_volume(track.mixer.gain_decibel),
                pan=track.mixer.pan,
                ai_singer_name=track.db_name or "",
                title=track.name or f"Track {i + 1}",
                note_list=note_list,
                edited_params=self.parse_params(track.parameters, note_list),
            )
            for i, track in enumerate(tracks)
            if (note_list := self.parse_notes(track.notes, track.db_defaults))
        ]

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
        self, s5p_notes: list[Optional[S5pNote]], db_defaults: S5pDbDefaults
    ) -> list[Note]:
        self.vibrato_value_interval_dict = PiecewiseIntervalDict()
        self.vibrato_coef_interval_dict = PiecewiseIntervalDict()
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
            if self.options.import_pitch:
                vibrato_start = self.synchronizer.get_actual_secs_from_ticks(note.start_pos) + (
                    s5p_note.t_f0_vbr_start
                    if s5p_note.t_f0_vbr_start is not None
                    else db_defaults.t_f0_vbr_start
                )
                vibrato_end = self.synchronizer.get_actual_secs_from_ticks(note.end_pos)
                if vibrato_end <= vibrato_start:
                    continue
                phase = s5p_note.p_f0_vbr if s5p_note.p_f0_vbr is not None else db_defaults.p_f0_vbr
                frequency = (
                    s5p_note.f_f0_vbr if s5p_note.f_f0_vbr is not None else db_defaults.f_f0_vbr
                )
                if phase is not None and frequency is not None:
                    self.vibrato_value_interval_dict[
                        portion.closedopen(vibrato_start, vibrato_end)
                    ] = functools.partial(
                        self.s5p_vibrato_value,
                        vibrato_start=vibrato_start,
                        phase=phase,
                        frequency=frequency,
                    )
                vibrato_attack_time = vibrato_start + (
                    s5p_note.t_f0_vbr_left
                    if s5p_note.t_f0_vbr_left is not None
                    else db_defaults.t_f0_vbr_left
                )
                vibrato_release_time = vibrato_end - (
                    s5p_note.t_f0_vbr_right
                    if s5p_note.t_f0_vbr_right is not None
                    else db_defaults.t_f0_vbr_right
                )
                vibrato_depth = (
                    s5p_note.d_f0_vbr if s5p_note.d_f0_vbr is not None else db_defaults.d_f0_vbr
                )
                self.vibrato_coef_interval_dict[
                    portion.closedopen(vibrato_start, vibrato_attack_time)
                ] = functools.partial(
                    linear_interpolation,  # type: ignore[call-arg]
                    start=(vibrato_start, 0),
                    end=(vibrato_attack_time, vibrato_depth),
                )
                self.vibrato_coef_interval_dict[
                    portion.closedopen(vibrato_attack_time, vibrato_release_time)
                ] = vibrato_depth
                self.vibrato_coef_interval_dict[
                    portion.closedopen(vibrato_release_time, vibrato_end)
                ] = functools.partial(
                    linear_interpolation,  # type: ignore[call-arg]
                    start=(vibrato_release_time, vibrato_depth),
                    end=(vibrato_end, 0),
                )
        return notes

    @staticmethod
    def s5p_vibrato_value(
        seconds: float, vibrato_start: float, frequency: float, phase: float
    ) -> float:
        return math.sin(math.pi * (2 * (seconds - vibrato_start) * frequency + phase))

    def parse_params(self, parameters: S5pParameters, note_list: list[Note]) -> Params:
        params = Params()
        if self.options.import_pitch:
            rel_pitch_points = self.parse_pitch_curve(
                parameters.pitch_delta, parameters.interval, note_list
            )
            pitch_simulator = PitchSimulator(
                synchronizer=self.synchronizer,
                portamento=PortamentoPitch.sigmoid_portamento(),
                note_list=note_list,
            )
            params.pitch = RelativePitchCurve(self.first_bar_length).to_absolute(
                rel_pitch_points, pitch_simulator
            )
        return params

    def parse_pitch_curve(
        self, pitch_delta: S5pPoints, interval: int, note_list: list[Note]
    ) -> list[Point]:
        pitch_raw_data = sortedcontainers.SortedList(key=operator.attrgetter("x"))
        for s5p_point_group in more_itertools.split_when(
            pitch_delta.root, lambda p1, p2: p2.offset > p1.offset + 1
        ):
            for is_first, is_last, s5p_point in more_itertools.mark_ends(s5p_point_group):
                if is_first and is_last:
                    continue
                point_ticks = round(s5p_point.offset * (interval / TICK_RATE))
                point_value = s5p_point.value
                pitch_raw_data.add(
                    Point(
                        x=point_ticks,
                        y=round(point_value),
                    )
                )
        points = []
        prev_pos = None
        value = None
        for pos, value in pitch_raw_data:
            pos_secs = self.synchronizer.get_actual_secs_from_ticks(pos)
            if prev_pos is not None:
                for interp_pos in range(prev_pos + 5, pos, 5):
                    interp_pos_secs = self.synchronizer.get_actual_secs_from_ticks(interp_pos)
                    if interp_value_diff := self.vibrato_value_interval_dict.get(
                        interp_pos_secs, 0
                    ):
                        interp_value_diff *= self.vibrato_coef_interval_dict[interp_pos_secs] * 2000
                    points.append(
                        Point(
                            x=interp_pos,
                            y=value + round(interp_value_diff),
                        )
                    )
            if value_diff := self.vibrato_value_interval_dict.get(pos_secs, 0):
                value_diff *= cast(float, self.vibrato_coef_interval_dict[pos_secs]) * 2000
            points.append(
                Point(
                    x=pos,
                    y=value + round(value_diff or 0),
                )
            )
            prev_pos = pos
        return points
