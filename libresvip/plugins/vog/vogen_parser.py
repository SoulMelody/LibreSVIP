import dataclasses

from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import (
    VogenNote,
    VogenProject,
    VogenTrack,
)
from .options import InputOptions


@dataclasses.dataclass
class VogenParser:
    options: InputOptions

    def parse_project(self, vogen_project: VogenProject) -> Project:
        return Project(
            song_tempo_list=self.parse_tempos(vogen_project.bpm0),
            time_signature_list=self.parse_time_signatures(vogen_project.time_sig0),
            track_list=self.parse_tracks(vogen_project.utts),
        )

    def parse_tempos(self, bpm0: float) -> list[SongTempo]:
        return [SongTempo(position=0, bpm=bpm0)]

    def parse_time_signatures(self, time_sig0: str) -> list[TimeSignature]:
        numerator, _, denominator = time_sig0.partition("/")
        return [TimeSignature(numerator=int(numerator), denominator=int(denominator))]

    def parse_tracks(self, utts: list[VogenTrack]) -> list[SingingTrack]:
        return [
            SingingTrack(
                title=utt.name,
                ai_singer_name=utt.singer_id,
                note_list=self.parse_notes(utt.notes),
            )
            for utt in utts
        ]

    def parse_notes(self, notes: list[VogenNote]) -> list[Note]:
        return [
            Note(
                start_pos=note.on,
                length=note.dur,
                lyric=note.lyric,
                pronunciation=note.rom,
                key_number=note.pitch,
            )
            for note in notes
        ]
