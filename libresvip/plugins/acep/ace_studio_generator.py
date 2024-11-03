import dataclasses
import math
import random
from collections.abc import Callable
from typing import Optional

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    Track,
)
from libresvip.model.point import Point
from libresvip.utils.audio import audio_track_info
from libresvip.utils.search import (
    binary_find_first,
    binary_find_last,
    find_last_index,
)

from .base_pitch_curve import BasePitchCurve
from .color_pool import count_color, get_color
from .enums import AcepLyricsLanguage
from .model import (
    AcepAudioPattern,
    AcepAudioTrack,
    AcepNote,
    AcepParamCurve,
    AcepParamCurveList,
    AcepParams,
    AcepProject,
    AcepSeedComposition,
    AcepTempo,
    AcepTimeSignature,
    AcepTrack,
    AcepVocalPattern,
    AcepVocalTrack,
)
from .options import OutputOptions, StrengthMappingOption
from .singers import DEFAULT_SEED, DEFAULT_SINGER_ID, singer2id, singer2seed


@dataclasses.dataclass
class AceGenerator:
    options: OutputOptions
    first_bar_tempo: list[SongTempo] = dataclasses.field(init=False)
    first_bar_ticks: int = dataclasses.field(init=False)
    ace_note_list: list[AcepNote] = dataclasses.field(init=False)
    pattern_start: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> AcepProject:
        ace_project = AcepProject()
        self.first_bar_ticks = int(project.time_signature_list[0].bar_length())
        self.first_bar_tempo = [
            tempo for tempo in project.song_tempo_list if tempo.position < self.first_bar_ticks
        ]
        denominator = project.time_signature_list[0].denominator
        numerator = project.time_signature_list[0].numerator
        ace_project.beats_per_bar = numerator * 4 // denominator
        if denominator <= 8 and numerator <= 8:
            ace_project.time_signatures = [
                AcepTimeSignature(bar_pos=0, numerator=numerator, denominator=denominator)
            ]
        self.synchronizer = TimeSynchronizer(project.song_tempo_list, self.first_bar_ticks)
        ace_project.tempos = self.generate_tempos(project.song_tempo_list)

        for track in project.track_list:
            if (ace_track := self.generate_track(track)) is not None:
                ace_project.tracks.append(ace_track)
        ace_project.duration = (
            max(
                (
                    len(ace_track)
                    for ace_track in ace_project.tracks
                    if isinstance(ace_track, AcepVocalTrack)
                ),
                default=0,
            )
        ) + 115200
        color_count = count_color()
        color_index = random.randint(0, color_count - 1)
        for ace_track in ace_project.tracks:
            ace_track.color = get_color(color_index)
            color_index = (color_index + 1) % color_count
        ace_project.color_index = color_index
        return ace_project

    def generate_tempos(self, tempos: list[SongTempo]) -> list[AcepTempo]:
        tempos = skip_tempo_list(tempos, self.first_bar_ticks)
        return [
            AcepTempo(
                bpm=tempo.bpm,
                position=tempo.position,
            )
            for tempo in tempos
        ]

    def generate_track(self, track: Track) -> Optional[AcepTrack]:
        if isinstance(track, InstrumentalTrack):
            ace_audio_track = AcepAudioTrack()
            audio_pattern = AcepAudioPattern(path=track.audio_file_path)
            audio_pattern.pos = self.synchronizer.get_actual_secs_from_ticks(track.offset)
            if (track_info := audio_track_info(track.audio_file_path)) is not None:
                audio_pattern.dur = track_info.duration / 1000
                audio_pattern.clip_dur = audio_pattern.dur - audio_pattern.clip_pos
            else:
                return None
            ace_audio_track.patterns.append(audio_pattern)
            ace_track = ace_audio_track
        elif isinstance(track, SingingTrack):
            ace_vocal_track = AcepVocalTrack(
                language=self.options.lyric_language,
            )
            if track.ai_singer_name in singer2id and track.ai_singer_name in singer2seed:
                ace_vocal_track.singer.singer_id = singer2id.get(
                    track.ai_singer_name, DEFAULT_SINGER_ID
                )
                ace_vocal_track.singer.composition.append(
                    AcepSeedComposition(code=singer2seed.get(track.ai_singer_name, DEFAULT_SEED))
                )
            else:
                ace_vocal_track.singer.singer_id = DEFAULT_SINGER_ID
                ace_vocal_track.singer.composition.append(AcepSeedComposition(code=DEFAULT_SEED))
            if len(track.note_list):
                buffer = [track.note_list[0]]

                def generate_vocal_pattern() -> None:
                    self.pattern_start = round(
                        max(
                            0,
                            buffer[0].start_pos - 240,
                        )
                    )
                    self.ace_note_list = []
                    for note in buffer:
                        if note.lyric:
                            self.generate_note(note)
                    vocal_pattern = AcepVocalPattern(
                        pos=self.pattern_start,
                        dur=round(buffer[-1].end_pos) - self.pattern_start,
                        notes=self.ace_note_list,
                    )
                    vocal_pattern.clip_dur = vocal_pattern.dur
                    buffer.clear()
                    if self.options.breath > 0:
                        self.adjust_breath_tags(vocal_pattern.notes)
                    vocal_pattern.parameters = self.generate_params(track.edited_params)
                    ace_vocal_track.patterns.append(vocal_pattern)

                for prev_note, cur_note in zip(track.note_list[:-1], track.note_list[1:]):
                    prev_end = prev_note.end_pos
                    cur_start = cur_note.start_pos
                    if cur_start - prev_end > self.options.split_threshold * TICKS_IN_BEAT > 0:
                        generate_vocal_pattern()
                    buffer.append(cur_note)
                if len(buffer):
                    generate_vocal_pattern()
            ace_track = ace_vocal_track
        else:
            return None
        ace_track.name = track.title
        ace_track.mute = track.mute
        ace_track.solo = track.solo
        ace_track.pan = track.pan
        ace_track.gain = min(6.0, 20 * math.log10(track.volume))
        return ace_track

    def adjust_breath_tags(self, notes: list[AcepNote]) -> None:
        for i in range(1, len(notes)):
            breath = notes[i].br_len
            if breath == 0:
                continue
            distance = self.synchronizer.get_duration_secs_from_ticks(
                notes[i - 1].pos, notes[i].pos
            )
            actual_breath = min(distance / 2, breath)
            notes[i - 1].dur = min(
                notes[i - 1].dur,
                int(
                    self.synchronizer.get_actual_ticks_from_secs_offset(
                        notes[i - 1].pos, distance - actual_breath
                    )
                )
                - notes[i - 1].pos,
            )
            notes[i].br_len -= actual_breath

    def generate_note(self, note: Note, pinyin: Optional[str] = None) -> None:
        if self.options.lyric_language == AcepLyricsLanguage.CHINESE and not pinyin:
            pinyin = next(iter(get_pinyin_series(note.lyric)), None)
        ace_note = AcepNote(
            pos=round(note.start_pos) - self.pattern_start,
            pitch=note.key_number,
            lyric=note.lyric,
            language=self.options.lyric_language,
        )
        ace_note.dur = round(note.end_pos - note.start_pos)

        if all(symbol not in note.lyric for symbol in ["-", "+"]):
            ace_note.pronunciation = (
                note.pronunciation if note.pronunciation is not None else pinyin or ""
            )
            if note.edited_phones is not None and note.edited_phones.head_length_in_secs >= 0:
                ace_note.head_consonants = [note.edited_phones.head_length_in_secs]
            elif self.options.default_consonant_length:
                ace_note.head_consonants = [self.options.default_consonant_length]
        elif (
            self.options.lyric_language in [AcepLyricsLanguage.ENGLISH, AcepLyricsLanguage.SPANISH]
            and ace_note.lyric == "+"
            and self.ace_note_list
        ):
            ace_note.pronunciation = "-"
            last_ace_note = self.ace_note_list[
                find_last_index(self.ace_note_list, lambda n: n.lyric != "-")
            ]
            lyric, sep, index = last_ace_note.lyric.partition("#")
            if sep == "#" and index.isdigit():
                ace_note.lyric = f"{lyric}#{int(index) + 1}"
            else:
                last_ace_note.lyric = f"{lyric}#1"
                ace_note.lyric = f"{lyric}#2"
        else:
            ace_note.lyric = ace_note.pronunciation = "-"

        if note.head_tag == "V" and self.options.breath > 0:
            breath_start_in_secs = (
                self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
                - self.options.breath / 1000
            )
            breath_start_in_ticks = self.synchronizer.get_actual_ticks_from_secs(
                breath_start_in_secs
            )
            ace_note.br_len = round(note.start_pos - breath_start_in_ticks)
        self.ace_note_list.append(ace_note)

    @staticmethod
    def linear_transform(
        lower_bound: float, middle_value: float, upper_bound: float
    ) -> Callable[[float], float]:
        def transform(x: float) -> float:
            if x >= 0:
                return x * (upper_bound - middle_value) / 1000 + middle_value
            else:
                return x * (middle_value - lower_bound) / 1000 + middle_value

        return transform

    def generate_params(self, parameters: Params) -> AcepParams:
        result = AcepParams(
            breathiness=self.generate_param_curves(
                parameters.breath, self.linear_transform(0.2, 1, 2.5)
            ),
            gender=self.generate_param_curves(parameters.gender, self.linear_transform(-1, 0, 1)),
        )
        result.pitch_delta = self.generate_pitch_curves(parameters.pitch)
        if self.options.map_strength_info == StrengthMappingOption.BOTH:
            result.energy = self.generate_param_curves(
                parameters.strength,
                lambda x: self.linear_transform(0, 1, 2)(x / 2),
            )
            result.tension = self.generate_param_curves(
                parameters.strength,
                lambda x: self.linear_transform(0.7, 1, 1.5)(x / 2),
            )
        elif self.options.map_strength_info == StrengthMappingOption.ENERGY:
            result.energy = self.generate_param_curves(
                parameters.strength, self.linear_transform(0, 1, 2)
            )
        elif self.options.map_strength_info == StrengthMappingOption.TENSION:
            result.tension = self.generate_param_curves(
                parameters.strength, self.linear_transform(0.7, 1, 1.5)
            )
        return result

    def generate_pitch_curves(self, curve: ParamCurve) -> AcepParamCurveList:
        ace_curves = AcepParamCurveList()
        base_pitch = BasePitchCurve(self.ace_note_list, self.synchronizer, self.pattern_start)
        left_bound = max(0, self.pattern_start + self.ace_note_list[0].pos - 240)
        right_bound = max(
            0,
            self.pattern_start + self.ace_note_list[-1].pos + self.ace_note_list[-1].dur + 120,
        )

        segments = []
        for seg in curve.split_into_segments(-100):
            if seg[-1].x < self.first_bar_ticks:
                continue
            start_ticks = seg[0].x - self.first_bar_ticks if seg[0].x > self.first_bar_ticks else 0
            end_ticks = seg[-1].x - self.first_bar_ticks
            if start_ticks <= right_bound and end_ticks >= left_bound:
                segments.append(seg)

        for segment in segments:
            start_point = (
                binary_find_last(
                    segment,
                    lambda point: (0 <= point.x - self.first_bar_ticks <= left_bound),
                )
                or segment[0]
            )
            end_point = (
                binary_find_first(
                    segment,
                    lambda point: (right_bound <= point.x - self.first_bar_ticks),
                )
                or segment[-1]
            )
            if start_point.x == end_point.x:
                continue
            ace_curve = AcepParamCurve(
                offset=round(start_point.x - self.first_bar_ticks - self.pattern_start)
            )
            curve_end = round(end_point.x - self.first_bar_ticks - self.pattern_start)
            tick_step = (end_point.x - start_point.x) / (curve_end - ace_curve.offset)
            tick = float(start_point.x)
            while tick < self.first_bar_ticks:
                ace_curve.offset += 1
                tick += tick_step
            tick = max(self.first_bar_ticks, tick)
            tick_step = (end_point.x - tick) / (curve_end - ace_curve.offset)
            while tick < left_bound:
                ace_curve.offset += 1
                tick += tick_step
            pos = ace_curve.offset
            while pos <= min(right_bound, curve_end):
                second = self.synchronizer.get_actual_secs_from_ticks(
                    round(tick - self.first_bar_ticks)
                )
                ace_curve.values.append(
                    self.get_value_from_segment(segment, tick) / 100
                    - base_pitch.semitone_value_at(second)
                )
                pos += 1
                tick += tick_step
            ace_curves.root.append(ace_curve)
        return ace_curves

    def generate_param_curves(
        self, curve: ParamCurve, mapping_func: Callable[[float], float]
    ) -> AcepParamCurveList:
        ace_curves = AcepParamCurveList()
        left_bound = max(0, self.pattern_start + self.ace_note_list[0].pos - 240)
        right_bound = max(
            0,
            self.pattern_start + self.ace_note_list[-1].pos + self.ace_note_list[-1].dur + 120,
        )
        segments = []
        for seg in curve.split_into_segments(-100):
            if seg[-1].x < self.first_bar_ticks:
                continue
            start_ticks = seg[0].x - self.first_bar_ticks if seg[0].x > self.first_bar_ticks else 0
            end_ticks = seg[-1].x - self.first_bar_ticks
            if start_ticks <= right_bound and end_ticks >= left_bound:
                segments.append(seg)
        for segment in segments:
            start_point = (
                binary_find_last(
                    segment,
                    lambda point: (0 <= point.x - self.first_bar_ticks <= left_bound),
                )
                or segment[0]
            )
            end_point = (
                binary_find_first(
                    segment,
                    lambda point: (right_bound <= point.x - self.first_bar_ticks),
                )
                or segment[-1]
            )
            ace_curve = AcepParamCurve(
                offset=round(start_point.x - self.first_bar_ticks - self.pattern_start)
            )
            curve_end = round(end_point.x - self.first_bar_ticks - self.pattern_start)
            tick_step = (end_point.x - start_point.x) / (curve_end - ace_curve.offset)
            tick = float(start_point.x)
            while tick < self.first_bar_ticks:
                ace_curve.offset += 1
                tick += tick_step
            tick = max(self.first_bar_ticks, tick)
            tick_step = (end_point.x - tick) / (curve_end - ace_curve.offset)
            while tick < left_bound:
                ace_curve.offset += 1
                tick += tick_step
            pos = ace_curve.offset
            while pos <= min(right_bound, curve_end):
                ace_curve.values.append(mapping_func(self.get_value_from_segment(segment, tick)))
                pos += 1
                tick += tick_step
            ace_curves.root.append(ace_curve)
        return ace_curves

    @staticmethod
    def get_value_from_segment(segment: list[Point], ticks: float) -> float:
        if (left_point := binary_find_last(segment, lambda point: point.x <= ticks)) is None:
            return segment[0].y
        if (right_point := binary_find_first(segment, lambda point: point.x > ticks)) is None:
            return segment[-1].y
        ratio = (ticks - left_point.x) / (right_point.x - left_point.x)
        return (1 - ratio) * left_point.y + ratio * right_point.y
