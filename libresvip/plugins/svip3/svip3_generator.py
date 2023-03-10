import dataclasses
from typing import List
from urllib.parse import urljoin

from pure_protobuf.types.google import Any_
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pydub.utils import ratio_to_db

from libresvip.core.time_sync import TimeSynchronizer
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

from .color_pool import random_color
from .constants import TYPE_URL_BASE, TrackType
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
from .singers import xstudio3_singers


@dataclasses.dataclass
class Svip3Generator:
    first_bar_length: int = dataclasses.field(init=False)
    song_tempo_list: List[SongTempo] = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    song_duration: int = dataclasses.field(default=0)

    def generate_project(self, project: Project) -> Svip3Project:
        return Svip3Project(
            beat_list=self.generate_time_signatures(project.time_signature_list),
            tempo_list=self.generate_song_tempos(project.song_tempo_list),
            track_list=self.generate_tracks(project.track_list),
            duration=self.song_duration,
        )

    def generate_time_signatures(
        self, time_signature_list: List[TimeSignature]
    ) -> List[Svip3SongBeat]:
        first_signature = time_signature_list[0]
        song_beat_list = [
            Svip3SongBeat(
                beat_size=Svip3BeatSize(
                    numerator=first_signature.numerator,
                    denominator=first_signature.denominator,
                ),
                pos=first_signature.bar_index,
            )
        ]
        self.first_bar_length = round(
            1920 * first_signature.numerator / first_signature.denominator
        )
        return song_beat_list

    def generate_song_tempos(
        self, song_tempo_list: List[SongTempo]
    ) -> List[Svip3SongTempo]:
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return [
            Svip3SongTempo(
                tempo=round(song_tempo.bpm * 100),
                pos=song_tempo.position,
            )
            for song_tempo in song_tempo_list
        ]

    def generate_tracks(self, track_list: List[Track]) -> List[Any_]:
        svip3_track_list = []
        for track in track_list:
            color = random_color()
            if isinstance(track, SingingTrack):
                svip3_track = self.generate_singing_track(track, color)
                type_url = urljoin(TYPE_URL_BASE, TrackType.SINGING_TRACK)
            elif isinstance(track, InstrumentalTrack):
                svip3_track = self.generate_instrumental_track(track, color)
                type_url = urljoin(TYPE_URL_BASE, TrackType.AUDIO_TRACK)
            else:
                continue
            svip3_track_container = Any_(
                type_url=type_url,
                value=svip3_track.dumps(),
            )
            svip3_track_list.append(svip3_track_container)
        return svip3_track_list

    def generate_instrumental_track(
        self, track: InstrumentalTrack, color: str
    ) -> Svip3AudioTrack:
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
        if volume > 0:
            return max(ratio_to_db(volume if volume > 0.01 else 0.01), -70)
        return -70

    @staticmethod
    def generate_pan(pan: float) -> float:
        return pan * 10.0

    def generate_audio_patterns(
        self, track: InstrumentalTrack
    ) -> List[Svip3AudioPattern]:
        kwargs = {}
        try:
            audio_segment = AudioSegment.from_file(track.audio_file_path)
            audio_duration_in_secs = audio_segment.duration_seconds
            audio_duration_in_ticks = self.synchronizer.get_actual_ticks_from_secs(
                audio_duration_in_secs
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
                self.song_duration = round(pattern_end + 1920)
        except (CouldntDecodeError, FileNotFoundError):
            pass
        patterns = []
        if kwargs:
            kwargs.update(
                {
                    "audio_file_path": track.audio_file_path,
                    "name": track.title,
                }
            )
            patterns.append(Svip3AudioPattern(**kwargs))
        return patterns

    def generate_singing_track(
        self, track: SingingTrack, color: str
    ) -> Svip3SingingTrack:
        return Svip3SingingTrack(
            name=track.title,
            color=color,
            mute=track.mute,
            solo=track.solo,
            volume=self.to_decibel_volume(track.volume),
            pan=self.generate_pan(track.pan),
            ai_singer_id=xstudio3_singers.get_uuid(track.ai_singer_name),
            pattern_list=self.generate_singing_patterns(track),
        )

    def generate_singing_patterns(
        self, track: SingingTrack
    ) -> List[Svip3SingingPattern]:
        last_note = track.note_list[-1]
        if last_note.end_pos > self.song_duration:
            self.song_duration = last_note.end_pos + 1920
        return [
            Svip3SingingPattern(
                name=track.title,
                real_pos=0,
                play_pos=0,
                real_dur=last_note.end_pos + 1920,
                play_dur=last_note.end_pos + 1920,
                is_mute=track.mute,
                note_List=self.generate_notes(track.note_list),
                edited_pitch_line=self.generate_pitch_param(track.edited_params.pitch),
            )
        ]

    def generate_notes(self, note_list: List[Note]) -> List[Svip3Note]:
        svip3_note_list = []
        for note in note_list:
            consonant_length = 0
            has_consonant = False
            if (
                note.edited_phones is not None
                and note.edited_phones.head_length_in_secs > 0
            ):
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
            svip3_note = Svip3Note(
                start_pos=note.start_pos,
                width_pos=note.length,
                key_index=note.key_number,
                lyric=note.lyric,
                pronouncing=note.pronunciation,
                consonant_len=consonant_length,
                has_consonant=has_consonant,
                sp_len=400 if note.head_tag == "V" else 0,
                sil_len=400 if note.head_tag == "0" else 0,
            )
            svip3_note_list.append(svip3_note)
        return svip3_note_list

    def generate_pitch_param(self, curve: ParamCurve) -> List[Svip3LineParamNode]:
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
