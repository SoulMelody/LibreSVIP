import dataclasses
import pathlib

from pyzipper import AESZipFile

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Phones,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import PocketSingerMetadata, PocketSingerNote, PocketSingerProject
from .options import InputOptions


@dataclasses.dataclass
class PocketSingerParser:
    options: InputOptions
    archive_file: AESZipFile
    path: pathlib.Path
    first_bar_length: int = dataclasses.field(init=False)
    project: PocketSingerProject = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, metadata: PocketSingerMetadata) -> Project:
        self.project = PocketSingerProject.model_validate_json(
            self.archive_file.read(metadata.ace_file_name)
        )
        song_tempo_list = self.parse_tempos()
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return Project(
            song_tempo_list=song_tempo_list,
            time_signature_list=self.parse_time_signatures(),
            track_list=self.parse_singing_tracks() + self.parse_instrumental_tracks(),
        )

    def parse_tempos(self) -> list[SongTempo]:
        return [SongTempo(bpm=self.project.song_info.bpm)]

    def parse_time_signatures(self) -> list[TimeSignature]:
        time_signatures = [
            TimeSignature(numerator=self.project.song_info.beat_of_bar, denominator=4)
        ]
        self.first_bar_length = round(time_signatures[0].bar_length())
        return time_signatures

    def parse_singing_tracks(self) -> list[SingingTrack]:
        singing_tracks: list[SingingTrack] = []
        for track in self.project.tracks:
            singing_track = SingingTrack(
                mute=track.mute,
                solo=track.solo,
                pan=track.pan,
                ai_singer_name=track.role_info.name,
                note_list=self.parse_notes(track.notes),
            )
            singing_tracks.append(singing_track)
        return singing_tracks

    def parse_notes(self, ps_notes: list[PocketSingerNote]) -> list[Note]:
        notes: list[Note] = []
        for ps_note in ps_notes:
            start_pos = self.synchronizer.get_actual_ticks_from_secs(ps_note.start_time)
            note = Note(
                lyric=ps_note.grapheme if ps_note.grapheme_index == 0 else "-",
                key_number=ps_note.pitch,
                start_pos=int(start_pos),
                length=int(
                    self.synchronizer.get_actual_ticks_from_secs(ps_note.end_time) - start_pos
                ),
            )
            if ps_note.br_note is not None:
                note.head_tag = "V"
            if ps_note.consonant_time_head:
                note.edited_phones = Phones(head_length_in_secs=ps_note.consonant_time_head[0])
            else:
                note.edited_phones = Phones(head_length_in_secs=0)
            notes.append(note)
        return notes

    def parse_instrumental_tracks(self) -> list[InstrumentalTrack]:
        instrumental_tracks: list[InstrumentalTrack] = []
        if self.options.import_instrumental_track and not hasattr(self.path, "protocol"):
            for bgm_track in self.project.bgm_info.tracks:
                audio_path = self.path.parent / f"{bgm_track.file_name}.{bgm_track.file_type}"
                if audio_path.exists():
                    instrumental_tracks.append(
                        InstrumentalTrack(
                            title=bgm_track.file_name,
                            mute=self.project.bgm_info.mute,
                            solo=self.project.bgm_info.solo,
                            audio_file_path=str(audio_path),
                            offset=self.synchronizer.get_actual_ticks_from_secs(
                                bgm_track.start_time
                            ),
                        )
                    )
        return instrumental_tracks
