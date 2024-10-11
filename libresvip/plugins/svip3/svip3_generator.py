import dataclasses
import re
from typing import Any
from urllib.parse import urljoin

import pypinyin
from google.protobuf import any_pb2

from libresvip.core.lyric_phoneme.chinese import CHINESE_RE
from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.music_math import ratio_to_db
from libresvip.utils.translation import gettext_lazy as _

from .color_pool import random_color
from .constants import (
    DEFAULT_SINGER_ID,
    MAX_NOTE_DURATION,
    MIN_NOTE_DURATION,
    TYPE_URL_BASE,
    Svip3TrackType,
)
from .model import (
    Svip3AudioPattern,
    Svip3AudioTrack,
    Svip3BeatSize,
    Svip3LineParamNode,
    Svip3Note,
    Svip3Project,
    Svip3SingingPattern,
    Svip3SingingTrack,
    Svip3SongBeat,
    Svip3SongTempo,
)
from .options import OutputOptions
from .singers import singers_data

PINYIN_PATTERN = re.compile(r"^[a-z]+$")


@dataclasses.dataclass
class Svip3Generator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    song_tempo_list: list[SongTempo] = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    song_duration: int = dataclasses.field(default=0)

    def generate_project(self, project: Project) -> Svip3Project:
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        return Svip3Project(
            beat_list=self.generate_time_signatures(project.time_signature_list),
            tempo_list=self.generate_song_tempos(project.song_tempo_list),
            track_list=self.generate_tracks(project.track_list),
            duration=self.song_duration,
        )

    @staticmethod
    def generate_time_signatures(
        time_signature_list: list[TimeSignature],
    ) -> list[Svip3SongBeat]:
        return [
            Svip3SongBeat(
                beat_size=Svip3BeatSize(
                    numerator=time_signature.numerator,
                    denominator=time_signature.denominator,
                ),
                pos=time_signature.bar_index,
            )
            for time_signature in time_signature_list
        ]

    def generate_song_tempos(self, song_tempo_list: list[SongTempo]) -> list[Svip3SongTempo]:
        song_tempo_list = skip_tempo_list(song_tempo_list, self.first_bar_length)
        return [
            Svip3SongTempo(
                tempo=round(song_tempo.bpm * 100),
                pos=song_tempo.position,
            )
            for song_tempo in song_tempo_list
        ]

    def generate_tracks(self, track_list: list[Track]) -> list[any_pb2.Any]:
        svip3_track_list = []
        for track in track_list:
            color = random_color()
            if isinstance(track, SingingTrack):
                svip3_track = self.generate_singing_track(track, color)
                type_url = urljoin(TYPE_URL_BASE, Svip3TrackType.SINGING_TRACK)
            elif isinstance(track, InstrumentalTrack):
                svip3_track = self.generate_instrumental_track(track, color)
                type_url = urljoin(TYPE_URL_BASE, Svip3TrackType.AUDIO_TRACK)
            else:
                continue
            svip3_track_container = any_pb2.Any(
                type_url=type_url,
                value=type(svip3_track).serialize(svip3_track),
            )
            svip3_track_list.append(svip3_track_container)
        return svip3_track_list

    def generate_instrumental_track(self, track: InstrumentalTrack, color: str) -> Svip3AudioTrack:
        return Svip3AudioTrack(
            name=track.title,
            color=color,
            mute=track.mute,
            solo=track.solo,
            volume=self.to_decibel_volume(track.volume),
            pan=self.generate_pan(track.pan),
            pattern_list=self.generate_audio_patterns(track),
        )

    @staticmethod
    def to_decibel_volume(volume: float) -> float:
        return max(ratio_to_db(max(volume, 0.01)), -70) if volume > 0 else -70

    @staticmethod
    def generate_pan(pan: float) -> float:
        return pan * 10.0

    def generate_audio_patterns(self, track: InstrumentalTrack) -> list[Svip3AudioPattern]:
        kwargs: dict[str, Any] = {}
        if (track_info := audio_track_info(track.audio_file_path)) is not None:
            audio_duration_in_ticks = round(
                self.synchronizer.get_actual_ticks_from_secs(track_info.duration / 1000)
            )
            kwargs["real_dur"] = kwargs["play_dur"] = audio_duration_in_ticks
            if track.offset >= 0:
                kwargs["play_pos"] = 0
                kwargs["real_pos"] = round(
                    self.synchronizer.get_actual_ticks_from_ticks(track.offset)
                )
            else:
                kwargs["play_pos"] = kwargs["real_dur"] - track.offset
                kwargs["play_pos"] = track.offset
                kwargs["real_pos"] = -track.offset
            pattern_end = kwargs["real_pos"] + kwargs["play_dur"]
            if pattern_end > self.song_duration:
                self.song_duration = round(pattern_end + self.first_bar_length)
        patterns = []
        if kwargs:
            kwargs |= {
                "audio_file_path": track.audio_file_path,
                "name": track.title,
            }
            patterns.append(Svip3AudioPattern(**kwargs))
        return patterns

    def generate_singing_track(self, track: SingingTrack, color: str) -> Svip3SingingTrack:
        return Svip3SingingTrack(
            name=track.title,
            color=color,
            mute=track.mute,
            solo=track.solo,
            volume=self.to_decibel_volume(track.volume),
            pan=self.generate_pan(track.pan),
            ai_singer_id=singers_data.inverse.get(track.ai_singer_name, DEFAULT_SINGER_ID),
            pattern_list=self.generate_singing_patterns(track),
        )

    def generate_singing_patterns(self, track: SingingTrack) -> list[Svip3SingingPattern]:
        if not track.note_list:
            return []
        last_note = track.note_list[-1]
        if last_note.end_pos > self.song_duration:
            self.song_duration = last_note.end_pos + self.first_bar_length
        return [
            Svip3SingingPattern(
                name=track.title,
                real_pos=0,
                play_pos=0,
                real_dur=last_note.end_pos + self.first_bar_length,
                play_dur=last_note.end_pos + self.first_bar_length,
                is_mute=track.mute,
                note_list=self.generate_notes(track.note_list),
                edited_pitch_line=self.generate_pitch_param(track.edited_params.pitch),
            )
        ]

    def generate_notes(self, note_list: list[Note]) -> list[Svip3Note]:
        svip3_note_list = []
        for note in note_list:
            consonant_length = 0
            has_consonant = False
            if note.edited_phones is not None and note.edited_phones.head_length_in_secs > 0:
                has_consonant = True
                phone_start_in_secs = (
                    self.synchronizer.get_actual_secs_from_ticks(note.start_pos)
                    - note.edited_phones.head_length_in_secs
                )
                phone_start_in_ticks = self.synchronizer.get_actual_ticks_from_secs(
                    phone_start_in_secs
                )
                consonant_length = round(
                    self.synchronizer.get_actual_ticks_from_ticks(note.start_pos)
                    - phone_start_in_ticks
                )
            if PINYIN_PATTERN.fullmatch(note.lyric) is not None:
                pronunciation = note.lyric
            elif note.pronunciation:
                pronunciation = note.pronunciation
            elif note.lyric and CHINESE_RE.fullmatch(note.lyric) is not None:
                pronunciation = " ".join(pypinyin.lazy_pinyin(note.lyric))
            else:
                pronunciation = note.pronunciation or note.lyric
            if note.lyric != "-" and PINYIN_PATTERN.fullmatch(pronunciation) is None:
                msg_prefix = _("Unsupported pinyin:")
                show_warning(f"{msg_prefix} {pronunciation}")
                pronunciation = ""
            note_duration = self.synchronizer.get_duration_secs_from_ticks(
                note.start_pos, note.end_pos
            )
            if note_duration < MIN_NOTE_DURATION:
                msg_prefix = _("Note duration is too short:")
                show_warning(f"{msg_prefix} {note.lyric}")
            elif note_duration > MAX_NOTE_DURATION:
                msg_prefix = _("Note duration is too long:")
                show_warning(f"{msg_prefix} {note.lyric}")
            svip3_note = Svip3Note(
                start_pos=note.start_pos,
                width_pos=note.length,
                key_index=note.key_number,
                lyric=note.lyric,
                pronouncing=pronunciation,
                consonant_len=consonant_length,
                has_consonant=has_consonant,
                sp_len=400 if note.head_tag == "V" else 0,
                sil_len=400 if note.head_tag == "0" else 0,
            )
            svip3_note_list.append(svip3_note)
        return svip3_note_list

    def generate_pitch_param(self, curve: ParamCurve) -> list[Svip3LineParamNode]:
        point_list = []
        splited_curves = curve.split_into_segments(-100)
        for segment in splited_curves:
            if not len(segment):
                continue
            prev_pos = 0
            left_interrupt = False
            for point in segment:
                if point.x == prev_pos:
                    continue
                if point.x < self.first_bar_length:
                    continue
                elif not left_interrupt:
                    left_interrupt = True
                    point_list.append(
                        Svip3LineParamNode(
                            pos=point.x - self.first_bar_length,
                            value=-1.0,
                        )
                    )
                pos = point.x - self.first_bar_length
                value = (point.y + 50) / 100
                point_list.append(
                    Svip3LineParamNode(
                        pos=pos,
                        value=float(value),
                    )
                )
                prev_pos = point.x
            last_point = segment[-1]
            point_list.append(
                Svip3LineParamNode(
                    pos=last_point.x - self.first_bar_length,
                    value=-1.0,
                )
            )
        return point_list
