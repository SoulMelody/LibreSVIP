import dataclasses
import operator
import re
from collections.abc import Callable
from functools import partial, reduce
from typing import Optional, cast

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.tick_counter import shift_beat_list, shift_tempo_list
from libresvip.core.time_interval import RangeInterval
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Phones,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point
from libresvip.utils.music_math import (
    clamp,
    cosine_easing_in_out_interpolation,
    cubic_interpolation,
    db_to_float,
    linear_interpolation,
    ratio_to_db,
)
from libresvip.utils.search import find_index

from .constants import TICK_RATE
from .interval_utils import position_to_ticks
from .model import (
    SVDatabase,
    SVGroup,
    SVMeter,
    SVNote,
    SVParamCurve,
    SVParameters,
    SVProject,
    SVTempo,
    SVTrack,
    SVVoice,
)
from .options import BreathOption, GroupOption, InputOptions, PitchOption
from .param_expression import CurveGenerator, ParamExpression, PitchGenerator
from .phoneme_utils import default_phone_marks, sv_g2p, xsampa2pinyin
from .track_merge_utils import track_override_with

clip = cast(Callable[[int], int], partial(clamp, lower=-1000, upper=1000))


@dataclasses.dataclass
class SynthVParser:
    options: InputOptions
    first_bar_tick: int = dataclasses.field(init=False)
    first_bpm: float = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    voice_settings: SVVoice = dataclasses.field(init=False)
    instant_pitch: SVParamCurve = dataclasses.field(init=False)
    group_library: dict[str, SVGroup] = dataclasses.field(default_factory=dict)
    group_split_counts: dict[str, int] = dataclasses.field(default_factory=dict)
    tracks_from_groups: list[Track] = dataclasses.field(default_factory=list)

    def actual_value_at(
        self,
        compound_expr: ParamExpression,
        mapping_func: Callable[[float], int],
        ticks: int,
    ) -> int:
        return clip(mapping_func(compound_expr.value_at_ticks(ticks) / 1000))

    @staticmethod
    def parse_interpolation(
        mode: str,
    ) -> Callable[[float, tuple[float, float], tuple[float, float]], float]:
        if mode == "cosine":
            return cosine_easing_in_out_interpolation
        elif mode == "cubic":
            return cubic_interpolation
        else:
            return linear_interpolation

    def parse_audio_offset(self, offset: int) -> int:
        if offset >= 0:
            return position_to_ticks(offset)
        return round(offset / TICK_RATE * self.first_bpm / DEFAULT_BPM)

    @staticmethod
    def parse_meter(meter: SVMeter) -> TimeSignature:
        return TimeSignature(
            bar_index=meter.index,
            numerator=meter.numerator,
            denominator=meter.denominator,
        )

    @staticmethod
    def parse_tempo(tempo: SVTempo) -> SongTempo:
        return SongTempo(position=position_to_ticks(tempo.position), bpm=tempo.bpm)

    @staticmethod
    def parse_volume(gain: float) -> float:
        if gain >= 0:
            return min(gain / (ratio_to_db(4)) + 1.0, 2.0)
        else:
            return db_to_float(gain)

    def parse_param_curve(
        self,
        sv_curve: SVParamCurve,
        mapping_func: Callable[[float], int],
        base_value: Optional[float] = None,
        master_curve: Optional[SVParamCurve] = None,
    ) -> ParamCurve:
        if base_value is None:
            base_value = 0.0
        curve = ParamCurve()
        interpolation_func = self.parse_interpolation(sv_curve.mode)
        decoded_base_value = mapping_func(base_value)

        generator = CurveGenerator(
            _point_list=[
                Point(
                    position_to_ticks(point.offset) + self.first_bar_tick,
                    mapping_func(point.value + base_value),
                )
                for point in sv_curve.points.root
            ],
            _interpolation=interpolation_func,
            _base_value=decoded_base_value,
        )
        if master_curve is None or not len(master_curve.points):
            curve.points.root = [
                Point(point.x, clip(point.y)) for point in generator.get_converted_curve(5)
            ]
            return curve
        if not len(sv_curve.points):
            master_generator = CurveGenerator(
                _point_list=[
                    Point(
                        position_to_ticks(point.offset) + self.first_bar_tick,
                        mapping_func(point.value + base_value),
                    )
                    for point in master_curve.points.root
                ],
                _interpolation=interpolation_func,
                _base_value=decoded_base_value,
            )
            curve.points.root = [
                Point(point.x, clip(point.y)) for point in master_generator.get_converted_curve(5)
            ]
            return curve
        group_expr = CurveGenerator(
            _point_list=[
                Point(
                    position_to_ticks(point.offset) + self.first_bar_tick,
                    round(point.value * 1000),
                )
                for point in sv_curve.points.root
            ],
            _interpolation=self.parse_interpolation(sv_curve.mode),
            _base_value=round(base_value * 1000),
        )
        master_expr = CurveGenerator(
            _point_list=[
                Point(
                    position_to_ticks(point.offset) + self.first_bar_tick,
                    round(point.value * 1000),
                )
                for point in master_curve.points.root
            ],
            _interpolation=self.parse_interpolation(master_curve.mode),
        )
        compound_expr = group_expr + master_expr
        group_points = group_expr.point_list
        master_points = master_expr.point_list

        i = j = 0
        if group_points[i].x < master_points[j].x:
            prev_point = group_points[i]
            i += 1
            prev_point_is_base = prev_point.y == round(base_value * 1000)
        else:
            prev_point = master_points[j]
            j += 1
            prev_point_is_base = prev_point.y == 0
        curve.points.append(Point.start_point(self.actual_value_at(compound_expr, mapping_func, 0)))
        curve.points.append(
            Point(
                prev_point.x,
                self.actual_value_at(compound_expr, mapping_func, prev_point.x),
            )
        )

        while i < len(group_points) or j < len(master_points):
            if i < len(group_points) and (
                j >= len(master_points) or group_points[i].x <= master_points[j].x
            ):
                current_point = group_points[i]
                i += 1
                current_point_is_base = current_point.y == round(base_value * 1000)
            else:
                current_point = master_points[j]
                j += 1
                current_point_is_base = current_point.y == 0
            if prev_point_is_base and current_point_is_base and prev_point.x <= current_point.x:
                curve.points.append(
                    Point(
                        prev_point.x,
                        self.actual_value_at(compound_expr, mapping_func, prev_point.x),
                    )
                )
                curve.points.append(
                    Point(
                        current_point.x,
                        self.actual_value_at(compound_expr, mapping_func, current_point.x),
                    )
                )
            else:
                for p in range(prev_point.x, current_point.x, 5):
                    curve.points.append(
                        Point(
                            p,
                            self.actual_value_at(compound_expr, mapping_func, p),
                        )
                    )
            prev_point = current_point
            prev_point_is_base = current_point_is_base
        curve.points.append(
            Point(
                prev_point.x,
                self.actual_value_at(compound_expr, mapping_func, prev_point.x),
            )
        )
        curve.points.append(
            Point.end_point(
                self.actual_value_at(compound_expr, mapping_func, prev_point.x),
            )
        )
        return curve

    def parse_pitch_curve(
        self,
        pitch_diff: SVParamCurve,
        vibrato_env: SVParamCurve,
        sv_notes: list[SVNote],
        step: int = 5,
        master_pitch_diff: Optional[SVParamCurve] = None,
        master_vibrato_env: Optional[SVParamCurve] = None,
    ) -> ParamCurve:
        curve = ParamCurve()
        if not sv_notes:
            curve.points.append(Point.start_point())
            curve.points.append(Point.end_point())
            return curve
        pitch_diff_expr: ParamExpression = CurveGenerator(
            _point_list=[
                Point(
                    position_to_ticks(point.offset),
                    round(point.value),
                )
                for point in pitch_diff.points.root
            ],
            _interpolation=self.parse_interpolation(pitch_diff.mode),
        )
        vibrato_env_expr: ParamExpression = CurveGenerator(
            _point_list=[
                Point(
                    position_to_ticks(point.offset),
                    round(point.value * 1000),
                )
                for point in vibrato_env.points.root
            ],
            _interpolation=self.parse_interpolation(vibrato_env.mode),
            _base_value=1000,
        )
        if master_pitch_diff is not None:
            pitch_diff_expr += CurveGenerator(
                _point_list=[
                    Point(
                        position_to_ticks(point.offset),
                        round(point.value),
                    )
                    for point in master_pitch_diff.points.root
                ],
                _interpolation=self.parse_interpolation(master_pitch_diff.mode),
            )
        if master_vibrato_env is not None:
            vibrato_env_expr += CurveGenerator(
                _point_list=[
                    Point(
                        position_to_ticks(point.offset),
                        round(point.value * 1000),
                    )
                    for point in master_vibrato_env.points.root
                ],
                _interpolation=self.parse_interpolation(vibrato_env.mode),
            )
        if self.options.instant:
            instant_interval = RangeInterval(
                [
                    (
                        position_to_ticks(note.onset),
                        position_to_ticks(note.onset + note.duration),
                    )
                    for note in sv_notes
                    if note.instant_mode is not False
                ]
            )
            pitch_diff_expr += CurveGenerator(
                interval=instant_interval.interval,
                _point_list=[
                    Point(
                        position_to_ticks(point.offset),
                        round(point.value),
                    )
                    for point in self.instant_pitch.points.root
                ],
                _interpolation=self.parse_interpolation(self.instant_pitch.mode),
            )
        interval = RangeInterval(
            [
                (
                    position_to_ticks(note.onset),
                    position_to_ticks(note.onset + note.duration),
                )
                for note in sv_notes
            ]
        ).expand(120)

        if self.options.pitch in {PitchOption.VIBRATO, PitchOption.PLAIN}:
            regard_default_vibrato_as_unedited = self.options.pitch == PitchOption.PLAIN
            pitch_interval = 0.1

            def reduced_interval(current: RangeInterval, note: SVNote) -> RangeInterval:
                start_secs = (
                    self.synchronizer.get_actual_secs_from_ticks(position_to_ticks(note.onset))
                    - max(0.0, note.attributes.transition_offset)
                    - pitch_interval
                )
                end_secs = (
                    self.synchronizer.get_actual_secs_from_ticks(
                        position_to_ticks(note.onset + note.duration)
                    )
                    + pitch_interval
                )
                return current | RangeInterval(
                    [
                        (
                            round(
                                self.synchronizer.get_actual_ticks_from_secs(max(0.0, start_secs))
                            ),
                            round(self.synchronizer.get_actual_ticks_from_secs(end_secs)),
                        )
                    ]
                )

            note_edited_range = reduce(
                reduced_interval,
                (
                    note
                    for note in sv_notes
                    if note.pitch_edited(
                        regard_default_vibrato_as_unedited,
                        self.options.instant,
                    )
                ),
                RangeInterval(),
            )
            param_edited_range = pitch_diff.edited_range() | vibrato_env.edited_range(1.0)
            if master_pitch_diff is not None:
                param_edited_range |= master_pitch_diff.edited_range()
            if master_vibrato_env is not None:
                param_edited_range |= master_vibrato_env.edited_range(1.0)
            interval &= note_edited_range | param_edited_range
        generator = PitchGenerator(
            _synchronizer=self.synchronizer,
            _note_list=sv_notes,
            _pitch_diff=pitch_diff_expr,
            _vibrato_env=vibrato_env_expr,
        )
        curve.points.append(Point.start_point())
        for start, end in interval.shift(self.first_bar_tick).sub_ranges():
            curve.points.append(Point(start, -100))
            curve.points.extend(
                Point(i, round(generator.value_at_ticks(i - self.first_bar_tick)))
                for i in range(start, end, step)
            )
            curve.points.append(
                Point(
                    end,
                    round(generator.value_at_ticks(end - self.first_bar_tick)),
                )
            )
            curve.points.append(Point(end, -100))
        curve.points.append(Point.end_point())
        return curve

    def parse_params(
        self,
        sv_params: SVParameters,
        sv_notes: list[SVNote],
        master_params: Optional[SVParameters] = None,
    ) -> Params:
        params = Params()
        if self.options.import_pitch:
            params.pitch = self.parse_pitch_curve(
                sv_params.pitch_delta,
                sv_params.vibrato_env,
                sv_notes,
                5,
                master_params.pitch_delta if master_params else None,
                master_params.vibrato_env if master_params else None,
            )
        if self.options.import_volume:
            params.volume = self.parse_param_curve(
                sv_params.loudness,
                lambda val: round(val / 12.0 * 1000.0)
                if val >= 0.0
                else round(1000 * db_to_float(val) - 1000),
                self.voice_settings.param_loudness or 0.0,
                master_params.loudness if master_params else None,
            )
        if self.options.import_breath:
            params.breath = self.parse_param_curve(
                sv_params.breathiness,
                lambda val: round(val * 1000),
                self.voice_settings.param_breathiness or 0.0,
                master_params.breathiness if master_params else None,
            )
        if self.options.import_gender:
            params.gender = self.parse_param_curve(
                sv_params.gender,
                lambda val: round(val * -1000),
                self.voice_settings.param_gender or 0.0,
                master_params.gender if master_params else None,
            )
        if self.options.import_strength:
            params.strength = self.parse_param_curve(
                sv_params.tension,
                lambda val: round(val * 1000),
                self.voice_settings.param_tension or 0.0,
                master_params.tension if master_params else None,
            )
        return params

    @staticmethod
    def parse_note(sv_note: SVNote, database: SVDatabase) -> Note:
        note = Note(
            start_pos=position_to_ticks(sv_note.onset),
            key_number=sv_note.pitch,
        )
        note.length = position_to_ticks(sv_note.onset + sv_note.duration) - note.start_pos
        note.lyric = SVNote.normalize_lyric(sv_note.lyrics)
        if sv_note.phonemes:
            note_default_language = sv_note.attributes.default_language(database)
            if note_default_language == "japanese":
                note.pronunciation = sv_note.phonemes
            elif note_default_language in ["mandarin", "cantonese"]:
                note.pronunciation = xsampa2pinyin(sv_note.phonemes, note_default_language)
        return note

    def parse_note_list(self, sv_note_list: list[SVNote], database: SVDatabase) -> list[Note]:
        note_list = []
        breath_pattern = re.compile(r"^\s*\.?\s*br(l?[1-9])?\s*$")
        if self.options.breath == BreathOption.CONVERT:
            if len(sv_note_list) > 1:
                prev_index = -1
                while (
                    current_offset := find_index(
                        sv_note_list[prev_index + 1 :],
                        lambda _note: breath_pattern.match(_note.lyrics) is None,
                    )
                ) != -1:
                    current_index = prev_index + current_offset + 1
                    note = self.parse_note(sv_note_list[current_index], database)
                    if current_index > prev_index + 1:
                        breath_note = sv_note_list[current_index - 1]
                        if (
                            position_to_ticks(sv_note_list[current_index].onset)
                            - position_to_ticks(breath_note.onset + breath_note.duration)
                        ) < 120:
                            note.head_tag = "V"
                    note_list.append(note)
                    prev_index = current_index
            elif len(sv_note_list) == 1 and breath_pattern.match(sv_note_list[0].lyrics) is None:
                note_list.append(self.parse_note(sv_note_list[0], database))
            sv_note_list = [
                note for note in sv_note_list if breath_pattern.match(note.lyrics) is None
            ]
        else:
            if self.options.breath == BreathOption.IGNORE:
                sv_note_list = [
                    note for note in sv_note_list if breath_pattern.match(note.lyrics) is None
                ]
            note_list = [self.parse_note(note, database) for note in sv_note_list]
        if len(sv_note_list):
            lyrics, languages = zip(
                *(
                    (
                        SVNote.normalize_phoneme(note),
                        sv_note.attributes.default_language(database),
                    )
                    for note, sv_note in zip(note_list, sv_note_list)
                )
            )
        else:
            lyrics, languages = (), ()
        lyrics_phoneme = sv_g2p(lyrics, languages)
        if not len(note_list):
            return note_list
        current_sv_note = sv_note_list[0]
        current_duration = current_sv_note.attributes.dur
        current_phone_marks = default_phone_marks(
            lyrics_phoneme[0],
            current_sv_note.attributes.default_language(database),
        )

        if (
            current_phone_marks[0] > 0
            and current_duration is not None
            and current_duration[0] != 1.0
        ):
            note_list[0].edited_phones = Phones(
                head_length_in_secs=min(1.8, current_duration[0] * current_phone_marks[0]),
            )

        for i in range(len(sv_note_list) - 1):
            next_sv_note = sv_note_list[i + 1]
            next_duration = next_sv_note.attributes.dur
            next_phone_marks = default_phone_marks(
                lyrics_phoneme[i + 1],
                next_sv_note.attributes.default_language(database),
            )

            index = 1 if next_phone_marks[0] > 0 else 0
            current_main_part_edited = (
                current_phone_marks[1] > 0
                and current_duration is not None
                and len(current_duration) > index
            )
            next_head_part_edited = (
                next_phone_marks[0] > 0 and next_duration is not None and len(next_duration)
            )
            if (
                current_main_part_edited
                and current_duration is not None
                and len(current_duration) > index + 1
            ):
                if note_list[i].edited_phones is None:
                    note_list[i].edited_phones = Phones(
                        mid_ratio_over_tail=(
                            current_phone_marks[1]
                            * current_duration[index]
                            / current_duration[index + 1]
                        )
                    )
                else:
                    note_list[i].edited_phones.mid_ratio_over_tail = (  #  type: ignore[union-attr]
                        current_phone_marks[1]
                        * current_duration[index]
                        / current_duration[index + 1]
                    )
            if (
                next_head_part_edited
                and current_duration is not None
                and next_phone_marks is not None
                and next_duration is not None
            ):
                if note_list[i + 1].edited_phones is None:
                    note_list[i + 1].edited_phones = Phones()
                space_in_secs = min(
                    2.0,
                    self.synchronizer.get_duration_secs_from_ticks(
                        note_list[i].start_pos + self.first_bar_tick,
                        note_list[i + 1].start_pos + self.first_bar_tick,
                    ),
                )
                length = next_phone_marks[0] * next_duration[0]
                if current_main_part_edited:
                    ratio = (
                        2 / (current_duration[index] + current_duration[index + 1])
                        if len(current_duration) > index + 1
                        else 1 / current_duration[index]
                    )
                    if length * ratio > self.synchronizer.get_duration_secs_from_ticks(
                        note_list[i].end_pos + self.first_bar_tick,
                        note_list[i + 1].start_pos + self.first_bar_tick,
                    ):
                        length *= ratio
                note_list[i + 1].edited_phones.head_length_in_secs = min(  #  type: ignore[union-attr]
                    0.9 * space_in_secs, length
                )
            current_duration = next_duration
            current_phone_marks = next_phone_marks
        idx = 1 if current_phone_marks[0] > 0 else 0
        if (
            current_phone_marks[1] > 0
            and current_duration is not None
            and len(current_duration) > idx + 1
        ):
            if note_list[-1].edited_phones is None:
                note_list[-1].edited_phones = Phones()
            note_list[-1].edited_phones.mid_ratio_over_tail = (
                current_phone_marks[1] * current_duration[idx] / current_duration[idx + 1]
            )
        return note_list

    def parse_track(self, sv_track: SVTrack) -> Optional[Track]:
        if sv_track.main_ref.is_instrumental:
            if self.options.import_instrumental_track and sv_track.main_ref.audio is not None:
                svip_track = InstrumentalTrack(
                    audio_file_path=sv_track.main_ref.audio.filename,
                    offset=self.parse_audio_offset(sv_track.main_ref.blick_offset),
                )
            else:
                return None
        else:
            self.voice_settings = sv_track.main_ref.voice
            master_note_attributes = self.voice_settings.to_attributes()
            if self.options.instant:
                self.instant_pitch = sv_track.main_ref.system_pitch_delta
            for note in sv_track.main_group.notes:
                note.merge_attributes(master_note_attributes)
            singing_track = SingingTrack(
                ai_singer_name=sv_track.main_ref.database.name,
                note_list=self.parse_note_list(
                    sv_track.main_group.notes, sv_track.main_ref.database
                ),
                edited_params=self.parse_params(
                    sv_track.main_group.parameters, sv_track.main_group.notes
                ),
            )
            if self.options.group == GroupOption.SPLIT:
                for sv_ref in sv_track.groups:
                    group = (
                        self.group_library[sv_ref.group_id] + sv_ref.blick_offset
                        ^ sv_ref.pitch_offset
                    )
                    voice_settings = sv_ref.voice
                    master_note_attributes = voice_settings.to_attributes()
                    if self.options.instant:
                        self.instant_pitch = sv_ref.system_pitch_delta
                    for note in group.notes:
                        note.merge_attributes(master_note_attributes)
                    self.group_split_counts[sv_ref.group_id] += 1
                    self.tracks_from_groups.append(
                        SingingTrack(
                            ai_singer_name=sv_ref.database.name,
                            title=f"{group.name} ({self.group_split_counts[sv_ref.group_id]})",
                            note_list=self.parse_note_list(group.notes, sv_ref.database),
                            edited_params=self.parse_params(
                                group.parameters,
                                group.notes,
                                sv_track.main_group.parameters,
                            ),
                        )
                    )
            elif self.options.group == GroupOption.MERGE:
                merged_group = sv_track.main_group
                for sv_ref in sv_track.groups:
                    group = (
                        self.group_library[sv_ref.group_id] + sv_ref.blick_offset
                        ^ sv_ref.pitch_offset
                    )
                    voice_settings = sv_ref.voice
                    master_note_attributes = voice_settings.to_attributes()
                    if self.options.instant:
                        self.instant_pitch = sv_ref.system_pitch_delta
                    for note in group.notes:
                        note.merge_attributes(master_note_attributes)
                    if merged_group.overlapped_with(group):
                        self.group_split_counts[sv_ref.group_id] += 1
                        self.tracks_from_groups.append(
                            SingingTrack(
                                ai_singer_name=sv_ref.database.name,
                                title=f"{group.name} ({self.group_split_counts[sv_ref.group_id]})",
                                note_list=self.parse_note_list(group.notes, sv_ref.database),
                                edited_params=self.parse_params(
                                    group.parameters,
                                    group.notes,
                                    sv_track.main_group.parameters,
                                ),
                            )
                        )
                    else:
                        track_override_with(
                            singing_track,
                            self.parse_note_list(group.notes, sv_ref.database),
                            self.parse_params(
                                group.parameters,
                                group.notes,
                                sv_track.main_group.parameters,
                            ),
                            self.first_bar_tick,
                        )
                        merged_group.notes.extend(group.notes)
                        merged_group.notes.sort(key=operator.attrgetter("onset"))
            svip_track = singing_track
        svip_track.title = sv_track.name
        svip_track.mute = sv_track.mixer.mute
        svip_track.solo = sv_track.mixer.solo
        svip_track.pan = sv_track.mixer.pan
        svip_track.volume = self.parse_volume(sv_track.mixer.gain_decibel)
        return svip_track

    def parse_project(self, sv_project: SVProject) -> Project:
        project = Project()
        time_sig = sv_project.time_sig
        self.first_bpm = time_sig.tempo[0].bpm

        project.time_signature_list = shift_beat_list(
            [self.parse_meter(meter) for meter in time_sig.meter], 1
        )
        self.first_bar_tick = round(project.time_signature_list[0].bar_length())
        project.song_tempo_list = shift_tempo_list(
            [self.parse_tempo(tempo) for tempo in time_sig.tempo],
            self.first_bar_tick,
        )
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)

        for sv_group in sv_project.library:
            self.group_library[sv_group.uuid] = sv_group
            self.group_split_counts[sv_group.uuid] = 0

        for sv_track in sv_project.tracks:
            if track := self.parse_track(sv_track):
                project.track_list.append(track)

        project.track_list.extend(self.tracks_from_groups)
        return project
