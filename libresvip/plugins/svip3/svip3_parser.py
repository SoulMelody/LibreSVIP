import dataclasses
from typing import Optional
from urllib.parse import urljoin

import regex as re

from libresvip.core.constants import DEFAULT_CHINESE_LYRIC, TICKS_IN_BEAT
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Phones,
    Point,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils import db_to_float, ratio_to_db

from .constants import TYPE_URL_BASE, TrackType
from .model import (
    Svip3AnyTrack,
    Svip3AudioTrack,
    Svip3Note,
    Svip3Project,
    Svip3SingingPattern,
    Svip3SingingTrack,
    Svip3SongBeat,
    Svip3SongTempo,
)
from .singers import xstudio3_singers


@dataclasses.dataclass
class Svip3Parser:
    first_bar_length: int = dataclasses.field(init=False)
    song_tempo_list: list[SongTempo] = dataclasses.field(init=False)

    def parse_project(self, svip3_project: Svip3Project) -> Project:
        time_signature_list = self.parse_time_signatures(svip3_project.beat_list)
        self.song_tempo_list = self.parse_song_tempos(svip3_project.tempo_list)
        tracks = self.parse_tracks(svip3_project.track_list)
        return Project(
            time_signature_list=time_signature_list,
            song_tempo_list=self.song_tempo_list,
            track_list=tracks,
        )

    def parse_time_signatures(
        self, beat_list: list[Svip3SongBeat]
    ) -> list[TimeSignature]:
        time_signature_list = []
        for beat in beat_list:
            time_signature_list.append(
                TimeSignature(
                    bar_index=beat.pos,
                    numerator=beat.beat_size.numerator,
                    denominator=beat.beat_size.denominator,
                )
            )
        self.first_bar_length = round(
            1920 * time_signature_list[0].numerator / time_signature_list[0].denominator
        )
        return time_signature_list

    @staticmethod
    def parse_song_tempos(tempo_list: list[Svip3SongTempo]) -> list[SongTempo]:
        song_tempo_list = []
        for tempo in tempo_list:
            song_tempo_list.append(
                SongTempo(
                    position=tempo.pos,
                    bpm=tempo.tempo / 100.0,
                )
            )
        return song_tempo_list

    def parse_tracks(self, track_list: list[Svip3AnyTrack]) -> list[Track]:
        tracks = []
        for track in track_list:
            if track.type_url == urljoin(TYPE_URL_BASE, TrackType.SINGING_TRACK):
                singing_track = Svip3SingingTrack.loads(track.value)
                tracks.append(self.parse_singing_track(singing_track))
            elif track.type_url == urljoin(TYPE_URL_BASE, TrackType.AUDIO_TRACK):
                audio_track = Svip3AudioTrack.loads(track.value)
                if xstudio_audio_track := self.parse_audio_track(audio_track):
                    tracks.append(xstudio_audio_track)
        return tracks

    def parse_audio_track(
        self, audio_track: Svip3AudioTrack
    ) -> Optional[InstrumentalTrack]:
        audio_file_path = None
        offset = 0
        if len(audio_track.pattern_list):
            first_pattern = audio_track.pattern_list[0]
            audio_file_path = first_pattern.audio_file_path
            offset = first_pattern.real_pos
        if audio_file_path is not None:
            return InstrumentalTrack(
                audio_file_path=audio_file_path,
                offset=offset,
                pan=self.parse_pan(audio_track.pan),
                title=audio_track.name,
                mute=audio_track.mute or False,
                solo=audio_track.solo or False,
                volume=self.to_linear_volume(audio_track.volume),
            )

    @staticmethod
    def parse_pan(pan: float) -> float:
        return (pan or 0) / 10.0

    @staticmethod
    def to_linear_volume(gain: float) -> float:
        if gain >= 0:
            return min(
                2.0,
                gain / ratio_to_db(4.0) + 1.0,
            )
        else:
            return db_to_float(gain)

    def parse_singing_track(self, singing_track: Svip3SingingTrack) -> SingingTrack:
        return SingingTrack(
            title=singing_track.name,
            mute=singing_track.mute,
            solo=singing_track.solo,
            volume=self.to_linear_volume(singing_track.volume),
            pan=self.parse_pan(singing_track.pan),
            ai_singer_name=xstudio3_singers.get_name(singing_track.ai_singer_id),
            note_list=self.parse_notes(singing_track.pattern_list),
            edited_params=self.parse_edited_params(singing_track.pattern_list),
        )

    def parse_notes(self, pattern_list: list[Svip3SingingPattern]) -> list[Note]:
        note_list = []
        for pattern in pattern_list:
            offset = pattern.real_pos
            left = pattern.play_pos + offset
            right = left + pattern.play_dur
            visible_notes = [
                note
                for note in pattern.note_list
                if left <= note.start_pos + offset <= right - note.width_pos
            ]
            for note in visible_notes:
                note_list.append(self.parse_note(note, offset))
        return note_list

    def parse_edited_params(self, pattern_list: list[Svip3SingingPattern]) -> Params:
        return Params(
            pitch=self.parse_pitch_curve(pattern_list),
        )

    def parse_note(self, svip3_note: Svip3Note, offset: int) -> Note:
        return Note(
            start_pos=svip3_note.start_pos + offset,
            length=svip3_note.width_pos,
            key_number=svip3_note.key_index,
            lyric=self.parse_lyric(svip3_note),
            pronunciation=self.parse_pronunciation(svip3_note),
            head_tag=self.parse_head_tag(svip3_note),
            edited_phones=self.parse_edited_phones(svip3_note),
        )

    @staticmethod
    def parse_lyric(svip3_note: Svip3Note) -> str:
        if re.search(r"[a-zA-Z]", svip3_note.lyric) is not None:
            return DEFAULT_CHINESE_LYRIC
        return svip3_note.lyric

    @staticmethod
    def parse_pronunciation(svip3_note: Svip3Note) -> str:
        if not svip3_note.pronouncing and "-" not in svip3_note.lyric:
            return svip3_note.lyric
        return svip3_note.pronouncing

    @staticmethod
    def parse_head_tag(svip3_note: Svip3Note) -> Optional[str]:
        if svip3_note.sil_len > 0:
            return "0"
        elif svip3_note.sp_len > 0:
            return "V"
        return None

    def parse_edited_phones(self, svip3_note: Svip3Note) -> Optional[Phones]:
        if svip3_note.consonant_len > 0:
            return Phones(
                head_length_in_secs=(
                    svip3_note.consonant_len
                    / TICKS_IN_BEAT
                    * 60.0
                    / self.song_tempo_list[0].bpm
                )
            )
        return None

    def parse_pitch_curve(self, pattern_list: list[Svip3SingingPattern]) -> ParamCurve:
        curves = []
        for pattern in pattern_list:
            curves.append(self.parse_pattern_curve(pattern))
        curve = ParamCurve()
        curve.points.append(Point.start_point())
        curve.points.root.extend(self.merge_param_curves(curves))
        curve.points.append(Point.end_point())
        return curve

    @staticmethod
    def merge_param_curves(curves: list[ParamCurve]) -> list[Point]:
        merged_curve = ParamCurve()
        for curve in curves:
            merged_curve.points.root.extend(curve.points.root)
        return merged_curve.points.root

    @staticmethod
    def get_visible_range(pattern: Svip3SingingPattern) -> tuple[int, int]:
        offset = pattern.real_pos
        left = pattern.play_pos + offset
        right = left + pattern.play_dur
        return left, right

    def parse_pattern_curve(self, pattern: Svip3SingingPattern) -> ParamCurve:
        curve = ParamCurve()
        offset = pattern.real_pos + self.first_bar_length
        left, right = self.get_visible_range(pattern)
        visible_nodes = [
            node
            for node in pattern.edited_pitch_line
            if left + self.first_bar_length
            <= node.pos + offset
            <= right + self.first_bar_length
        ]
        for node in visible_nodes:
            pos = node.pos + offset
            val = round(node.value * 100 - 50) if node.value != -1.0 else -100
            curve.points.append(Point(pos, val))
        return curve
