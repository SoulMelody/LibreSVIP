import dataclasses
import math
import operator
import re
from collections.abc import Callable
from typing import Optional

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.warning_types import show_warning
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
from libresvip.utils.music_math import clamp

from .base_pitch_curve import BasePitchCurve
from .model import (
    AcepAudioTrack,
    AcepLyricsLanguage,
    AcepNote,
    AcepParamCurveList,
    AcepParams,
    AcepProject,
    AcepTempo,
    AcepTrack,
    AcepVocalTrack,
)
from .options import InputOptions, NormalizationMethod
from .singers import id2singer
from .time_utils import tick_to_second

ACEP_ENGLISH_SPAN_RE = re.compile(r"#(\d+)$")


@dataclasses.dataclass
class AceParser:
    options: InputOptions
    content_version: int = dataclasses.field(init=False)
    ace_tempo_list: list[AcepTempo] = dataclasses.field(init=False)
    first_bar_ticks: int = dataclasses.field(init=False)

    def parse_project(self, ace_project: AcepProject) -> Project:
        project = Project()
        self.content_version = ace_project.version
        self.ace_tempo_list = ace_project.tempos
        if ace_project.time_signatures:
            project.time_signature_list = [
                TimeSignature(
                    bar_index=ace_time_sig.bar_pos,
                    numerator=ace_time_sig.numerator,
                    denominator=ace_time_sig.denominator,
                )
                for ace_time_sig in ace_project.time_signatures
            ]
        else:
            project.time_signature_list.append(
                TimeSignature(bar_index=0, numerator=ace_project.beats_per_bar, denominator=4)
            )
        self.first_bar_ticks = TICKS_IN_BEAT * ace_project.beats_per_bar
        project.song_tempo_list = skip_tempo_list(
            tempo_list=[self.parse_tempo(ace_tempo) for ace_tempo in ace_project.tempos],
            skip_ticks=self.first_bar_ticks,
        )
        for ace_track in ace_project.tracks:
            ace_track.gain += ace_project.master.gain
        for ace_track in ace_project.tracks:
            if (track := self.parse_track(ace_track)) is not None:
                project.track_list.append(track)
        return project

    @staticmethod
    def parse_tempo(ace_tempo: AcepTempo) -> SongTempo:
        return SongTempo(position=ace_tempo.position, bpm=ace_tempo.bpm)

    def parse_track(self, ace_track: AcepTrack) -> Optional[Track]:
        if (
            self.options.import_instrumental_track
            and isinstance(ace_track, AcepAudioTrack)
            and len(ace_track.patterns)
        ):
            track = InstrumentalTrack(audio_file_path=ace_track.patterns[0].path)
        elif isinstance(ace_track, AcepVocalTrack):
            track = SingingTrack(
                ai_singer_name=(id2singer.get(ace_track.singer.singer_id, None) or "")
            )
            ace_note_list = []
            ace_params = AcepParams()
            for pattern in ace_track.patterns:
                if len(pattern.notes) == 0:
                    continue
                ace_notes = [
                    note
                    for note in pattern.notes
                    if note.pos + pattern.pos >= 0
                    and pattern.clip_pos <= note.pos < pattern.clip_pos + pattern.clip_dur
                ]
                prev_ace_note = None
                for ace_note in ace_notes:
                    ace_note.dur = min(
                        ace_note.dur, pattern.clip_pos + pattern.clip_dur - ace_note.pos
                    )
                    ace_note.pos += pattern.pos
                    if (
                        prev_ace_note is not None
                        and prev_ace_note.pos + prev_ace_note.dur > ace_note.pos
                    ):
                        prev_ace_note.dur = ace_note.pos - prev_ace_note.pos
                    prev_ace_note = ace_note
                ace_note_list.extend(ace_notes)

                def merge_curves(src: AcepParamCurveList, dst: AcepParamCurveList) -> None:
                    for curve in src.root:
                        if curve.curve_type == "anchor":
                            curve.points2values()
                    ace_curves = [
                        curve
                        for curve in src.root
                        if curve.offset + pattern.pos >= -self.first_bar_ticks
                        and curve.offset + len(curve.values) > pattern.clip_pos
                        and curve.offset < pattern.clip_pos + pattern.clip_dur
                    ]
                    for ace_curve in ace_curves:
                        max_length = pattern.clip_pos + pattern.clip_dur - ace_curve.offset
                        if max_length < len(ace_curve.values):
                            ace_curve.values = ace_curve.values[:max_length]
                        ace_curve.offset += pattern.pos
                    dst.root.extend(ace_curves)

                merge_curves(pattern.parameters.pitch_delta, ace_params.pitch_delta)
                merge_curves(pattern.parameters.breathiness, ace_params.breathiness)
                merge_curves(pattern.parameters.gender, ace_params.gender)
                merge_curves(pattern.parameters.energy, ace_params.energy)
                merge_curves(pattern.parameters.tension, ace_params.tension)
                if self.options.breath_normalization.enabled:
                    merge_curves(pattern.parameters.real_breathiness, ace_params.real_breathiness)
                if self.options.tension_normalization.enabled:
                    merge_curves(pattern.parameters.real_tension, ace_params.real_tension)
                if self.options.energy_normalization.enabled:
                    merge_curves(pattern.parameters.real_energy, ace_params.real_energy)
            ace_note_list.sort(key=operator.attrgetter("pos"))
            track.note_list = [self.parse_note(ace_note) for ace_note in ace_note_list]
            track.edited_params = self.parse_params(ace_params, ace_note_list)
        else:
            return None
        track.title = ace_track.name
        track.mute = ace_track.mute
        track.solo = ace_track.solo
        track.volume = 10 ** (ace_track.gain / 20)
        return track

    def parse_note(self, ace_note: AcepNote, pinyin: Optional[str] = None) -> Note:
        if (
            not self.options.keep_all_pronunciation
            and ace_note.language == AcepLyricsLanguage.CHINESE
            and pinyin is None
        ):
            pinyin = next(iter(get_pinyin_series(ace_note.lyric)), None)
        note = Note(
            key_number=ace_note.pitch,
            start_pos=ace_note.pos,
            length=ace_note.dur,
            lyric=ace_note.lyric,
        )
        if (
            ace_note.language == AcepLyricsLanguage.ENGLISH
            and (english_span := ACEP_ENGLISH_SPAN_RE.search(note.lyric)) is not None
        ):
            span_index = int(english_span.group(1))
            if span_index == 1:
                note.lyric = ACEP_ENGLISH_SPAN_RE.sub("", note.lyric)
            else:
                note.lyric = "+"
        if pinyin is None or "-" not in ace_note.lyric and ace_note.pronunciation != pinyin:
            note.pronunciation = ace_note.pronunciation
        if ace_note.br_len > 0:
            note.head_tag = "V"
        if ace_note.head_consonants:
            note.edited_phones = Phones(
                head_length_in_secs=(
                    tick_to_second(note.start_pos, self.ace_tempo_list)
                    - tick_to_second(
                        note.start_pos - ace_note.head_consonants[0],
                        self.ace_tempo_list,
                    )
                )
            )
        return note

    def parse_params(self, ace_params: AcepParams, ace_note_list: list[AcepNote]) -> Params:
        def linear_transform(
            lower_bound: float, middle_value: float, upper_bound: float
        ) -> Callable[[float], int]:
            return lambda x: clamp(
                round(
                    (x - middle_value) / (upper_bound - middle_value) * 1000
                    if x >= middle_value
                    else (x - middle_value) / (middle_value - lower_bound) * 1000
                ),
                -1000,
                1000,
            )

        if self.options.breath_normalization.enabled:
            normalized = ace_params.real_breathiness.exclude(
                lambda x: (
                    x + 1e-3 < self.options.breath_normalization.lower_threshold
                    or x - 1e-3 > self.options.breath_normalization.upper_threshold
                )
            )
            if self.options.breath_normalization.normalize_method == NormalizationMethod.ZSCORE:
                normalized = normalized.z_score_normalize(
                    self.options.breath_normalization.scale,
                    self.options.breath_normalization.bias,
                )
            elif self.options.breath_normalization.normalize_method == NormalizationMethod.MINMAX:
                normalized = normalized.minmax_normalize(
                    self.options.breath_normalization.scale,
                    self.options.breath_normalization.bias,
                )
            else:
                msg = f"Unknown normalization method: {self.options.breath_normalization.normalize_method}"
                show_warning(msg)

            ace_params.breathiness = ace_params.breathiness.plus(
                normalized, 1.0, lambda x: x * 1.5 if x >= 0 else x * 0.8
            )

        if self.options.tension_normalization.enabled:
            normalized = ace_params.real_tension.exclude(
                lambda x: (
                    x + 1e-3 < self.options.tension_normalization.lower_threshold
                    or x - 1e-3 > self.options.tension_normalization.upper_threshold
                )
            )
            if self.options.tension_normalization.normalize_method == NormalizationMethod.ZSCORE:
                normalized = normalized.z_score_normalize(
                    self.options.tension_normalization.scale,
                    self.options.tension_normalization.bias,
                )
            elif self.options.tension_normalization.normalize_method == NormalizationMethod.MINMAX:
                normalized = normalized.minmax_normalize(
                    self.options.tension_normalization.scale,
                    self.options.tension_normalization.bias,
                )
            else:
                msg = f"Unknown normalization method: {self.options.tension_normalization.normalize_method}"
                show_warning(msg)

            ace_params.tension = ace_params.tension.plus(
                normalized, 1.0, lambda x: x * 0.5 if x >= 0 else x * 0.3
            )

        if self.options.energy_normalization.enabled:
            normalized = ace_params.real_energy.exclude(
                lambda x: (
                    x + 1e-3 < self.options.energy_normalization.lower_threshold
                    or x - 1e-3 > self.options.energy_normalization.upper_threshold
                )
            )
            if self.options.energy_normalization.normalize_method == NormalizationMethod.ZSCORE:
                normalized = normalized.z_score_normalize(
                    self.options.energy_normalization.scale,
                    self.options.energy_normalization.bias,
                )
            elif self.options.energy_normalization.normalize_method == NormalizationMethod.MINMAX:
                normalized = normalized.minmax_normalize(
                    self.options.energy_normalization.scale,
                    self.options.energy_normalization.bias,
                )
            else:
                msg = f"Unknown normalization method: {self.options.energy_normalization.normalize_method}"
                show_warning(msg)

            ace_params.energy = ace_params.energy.plus(normalized, 1.0, lambda x: x)

        parameters = Params()
        if self.options.import_pitch:
            parameters.pitch = self.parse_pitch_curve(ace_params.pitch_delta, ace_note_list)
        if self.options.import_breath:
            parameters.breath = self.parse_param_curve(
                ace_params.breathiness, linear_transform(0.2, 1, 2.5)
            )
        if self.options.import_gender:
            parameters.gender = self.parse_param_curve(
                ace_params.gender, linear_transform(-1, 0, 1)
            )
        if self.options.import_tension and self.options.import_energy:
            transform = linear_transform(0, 1, 2)
            parameters.volume = self.parse_param_curve(
                ace_params.energy, lambda x: round(self.options.energy_coefficient * transform(x))
            )
            remaining_energy = ace_params.energy.model_copy(
                deep=True,
                update={
                    "root": [
                        part.model_copy(
                            deep=True,
                            update={
                                "values": [
                                    (value - 1) * (1 - self.options.energy_coefficient) + 1
                                    for value in part.values
                                ]
                            },
                        )
                        for part in ace_params.energy.root
                    ]
                },
            )
            energy_plus_tension = remaining_energy.plus(
                ace_params.tension, 1.0, lambda x: (x - 1) * 0.5 if x >= 1 else (x - 1) * 0.3
            )
            parameters.strength = self.parse_param_curve(
                energy_plus_tension, lambda x: round(self.options.energy_coefficient * transform(x))
            )
        elif self.options.import_tension:
            parameters.strength = self.parse_param_curve(
                ace_params.tension, linear_transform(0.7, 1, 1.5)
            )
        elif self.options.import_energy:
            transform = linear_transform(0, 1, 2)
            parameters.volume = self.parse_param_curve(
                ace_params.energy, lambda x: round(self.options.energy_coefficient * transform(x))
            )
            parameters.strength = self.parse_param_curve(
                ace_params.energy,
                lambda x: round((1 - self.options.energy_coefficient) * transform(x)),
            )
        return parameters

    def parse_pitch_curve(
        self, ace_curves: AcepParamCurveList, ace_note_list: list[AcepNote]
    ) -> ParamCurve:
        curve = ParamCurve()
        curve.points.append(Point.start_point())
        if len(ace_curves.root) > 0:
            base_pitch = BasePitchCurve(
                notes=ace_note_list,
                tempos=self.ace_tempo_list,
            )
            for ace_curve in ace_curves.root:
                pos = ace_curve.offset
                curve.points.append(Point(pos + self.first_bar_ticks, -100))
                if ace_curve.curve_type == "anchor":
                    for value in ace_curve.values:
                        curve.points.append(Point(pos + self.first_bar_ticks, round(value * 100)))
                        pos += 1
                else:
                    for value in ace_curve.values:
                        if not math.isnan(value):
                            abs_semitone = (
                                base_pitch.semitone_value_at(
                                    tick_to_second(pos, self.ace_tempo_list)
                                )
                                + value
                            )
                            curve.points.append(
                                Point(pos + self.first_bar_ticks, round(abs_semitone * 100))
                            )
                        pos += 1
                curve.points.append(Point(pos - 1 + self.first_bar_ticks, -100))
        curve.points.append(Point.end_point())
        if self.options.curve_sample_interval > 0:
            curve = curve.reduce_sample_rate(self.options.curve_sample_interval, -100)
        return curve

    def parse_param_curve(
        self, ace_curves: AcepParamCurveList, mapping_func: Callable[[float], int]
    ) -> ParamCurve:
        curve = ParamCurve()
        curve.points.append(Point.start_point(0))
        for ace_curve in ace_curves.root:
            pos = ace_curve.offset
            curve.points.append(Point(x=pos + self.first_bar_ticks, y=0))
            for value in ace_curve.values:
                curve.points.append(Point(x=pos + self.first_bar_ticks, y=mapping_func(value)))
                pos += 1
            curve.points.append(Point(x=pos - 1 + self.first_bar_ticks, y=0))
        curve.points.append(Point.end_point(0))
        if self.options.curve_sample_interval > 0:
            curve = curve.reduce_sample_rate(self.options.curve_sample_interval)
        return curve
