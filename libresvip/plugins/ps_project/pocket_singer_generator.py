import dataclasses
import hashlib
import io
import pathlib
from typing import Optional

import more_itertools

from libresvip.core.constants import DEFAULT_CHINESE_LYRIC, TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import InstrumentalTrack, Note, Params, Project, SingingTrack, SongTempo
from libresvip.utils.audio import audio_track_info

from .enums import PocketSingerLyricsLanguage
from .model import (
    PocketSingerBgmInfo,
    PocketSingerBgmTrack,
    PocketSingerMetadata,
    PocketSingerNote,
    PocketSingerPitchBend,
    PocketSingerProject,
    PocketSingerSongInfo,
    PocketSingerTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class PocketSingerGenerator:
    options: OutputOptions
    buffer: io.BytesIO = dataclasses.field(default_factory=io.BytesIO)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> PocketSingerMetadata:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = TICKS_IN_BEAT * 4
        song_info = self.generate_song_info(project.song_tempo_list[0])
        ps_project = PocketSingerProject(song_info=song_info)
        if (
            first_instrumental_track := next(
                (track for track in project.track_list if isinstance(track, InstrumentalTrack)),
                None,
            )
        ) and (bgm_info := self.generate_bgm_info(first_instrumental_track)):
            ps_project.bgm_info = bgm_info
        ps_project.tracks.extend(
            self.generate_track(track)
            for track in project.track_list
            if isinstance(track, SingingTrack)
        )
        self.buffer.write(
            ps_project.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
        )
        return PocketSingerMetadata(ace_file_name="ps_structure.ps")

    def generate_song_info(self, tempo: SongTempo) -> PocketSingerSongInfo:
        return PocketSingerSongInfo(
            start=0,
            first_beat_offset=0.0,
            scale=[
                80,
                79,
                77,
                76,
                75,
                74,
                73,
                72,
                71,
                70,
                69,
                68,
                67,
                66,
                65,
                64,
                63,
                62,
                61,
                60,
                59,
                58,
                57,
                56,
                55,
                54,
                53,
                52,
                51,
                50,
                49,
                48,
                43,
            ],
            key="C",
            segment_of_beat=2,
            operate_scale=[72, 71, 69, 67, 65, 64, 62, 60, 59, 57, 55],
            bpm=tempo.bpm,
            name=self.options.title,
            duration=0.0,
            beat_of_bar=4,
        )

    def generate_bgm_info(
        self, instrumental_track: InstrumentalTrack
    ) -> Optional[PocketSingerBgmInfo]:
        audio_path = pathlib.Path(instrumental_track.audio_file_path)
        file_type = audio_path.suffix[1:].lower()
        if file_type not in ("wav", "mp3", "flac", "aac", "m4a"):
            return None
        if not (track_info := audio_track_info(audio_path)):
            return None
        audio_content = audio_path.read_bytes()
        self.audio_paths[audio_path.name] = audio_path
        audio_position = self.synchronizer.get_actual_secs_from_ticks(instrumental_track.offset)
        return PocketSingerBgmInfo(
            mute=instrumental_track.mute,
            solo=instrumental_track.solo,
            tracks=[
                PocketSingerBgmTrack(
                    file_name=audio_path.stem,
                    file_type=file_type,
                    file_md5=hashlib.md5(audio_content).hexdigest(),
                    position=audio_position,
                    start_time=audio_position,
                    end_time=audio_position + track_info.duration / 1000,
                )
            ],
        )

    def generate_track(self, track: SingingTrack) -> PocketSingerTrack:
        ps_track = PocketSingerTrack(
            language=self.options.lyric_language,
            mute=track.mute,
            solo=track.solo,
            pan=track.pan,
            sound_effect=0,
            singer_volume=1,
        )
        patched_notes = self.patch_notes(track.note_list)
        ps_notes, ps_track.lyric = self.generate_notes(patched_notes, track.edited_params)
        ps_track.notes.extend(ps_notes)
        return ps_track

    def patch_notes(self, notes: list[Note]) -> list[Note]:
        prev_note = None
        patched_notes = []
        for note in notes:
            if not note.lyric:
                continue
            elif note.lyric in ["-", "+"] and prev_note is not None:
                if note.start_pos == prev_note.end_pos:
                    note.key_number = prev_note.key_number
                    if note.lyric == "-":
                        prev_note.length += note.length
                        continue
                    else:
                        patched_notes.append(note)
                else:
                    prev_note = None
                    continue
            else:
                patched_notes.append(note)
            prev_note = note
        return patched_notes

    def generate_notes(
        self, notes: list[Note], params: Params
    ) -> tuple[list[PocketSingerNote], str]:
        ps_notes = []
        lyrics = []
        for note_group in more_itertools.split_when(
            notes,
            lambda prev_note, note: note.lyric != "+",
        ):
            group_lyric = note_group[0].lyric
            for i, note in enumerate(note_group):
                ps_note = PocketSingerNote(
                    language=self.options.lyric_language,
                    grapheme_count=len(note_group),
                    grapheme_index=i,
                    grapheme=group_lyric,
                    pitch=note.key_number,
                    start_time=self.synchronizer.get_actual_secs_from_ticks(note.start_pos),
                    end_time=self.synchronizer.get_actual_secs_from_ticks(note.end_pos),
                )
                if (
                    self.options.lyric_language != PocketSingerLyricsLanguage.ENGLISH
                    and len(group_lyric) == 1
                ):
                    lyrics.append(group_lyric)
                else:
                    lyrics.append(DEFAULT_CHINESE_LYRIC)
                if note.edited_phones is not None:
                    ps_note.consonant_time_head = [note.edited_phones.head_length_in_secs]
                for point in params.pitch.points.root:
                    if note.start_pos <= point.x - self.first_bar_length <= note.end_pos:
                        ps_note.pitch_bends.append(
                            PocketSingerPitchBend(
                                time=self.synchronizer.get_actual_secs_from_ticks(
                                    point.x - self.first_bar_length
                                ),
                                pitch=(point.y / 100 - note.key_number) if point.y != -100 else 0,
                            )
                        )
                ps_notes.append(ps_note)
        return ps_notes, "".join(lyrics)
