import dataclasses

import pypinyin

from libresvip.model.base import (
    Note,
    Params,
    Point,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import Y77Note, Y77Project
from .options import InputOptions


@dataclasses.dataclass
class Y77Parser:
    options: InputOptions

    def parse_project(self, y77_project: Y77Project) -> Project:
        project = Project(
            SongTempoList=self.parse_tempos(y77_project.bpm),
            TimeSignatureList=self.parse_time_signatures(y77_project),
            TrackList=self.parse_tracks(y77_project.notes),
        )
        return project

    def parse_tempos(self, bpm: float) -> list[SongTempo]:
        return [SongTempo(BPM=bpm, Position=0)]

    def parse_time_signatures(self, y77_project: Y77Project) -> list[TimeSignature]:
        return [
            TimeSignature(
                Numerator=y77_project.bbar,
                Denominator=y77_project.bbeat,
            )
        ]

    def parse_tracks(self, notes: list[Y77Note]) -> list[SingingTrack]:
        return [
            SingingTrack(
                AISingerName="元七七",
                NoteList=self.parse_notes(notes),
                EditedParams=self.parse_params(notes),
            )
        ]

    def parse_notes(self, notes: list[Y77Note]) -> list[Note]:
        note_list = []
        for y77_note in notes:
            note = Note(
                Lyric=y77_note.lyric,
                StartPos=y77_note.start * 30,
                Length=y77_note.len * 30,
                KeyNumber=88 - y77_note.pitch,
            )
            phonemes = pypinyin.pinyin(
                y77_note.lyric, heteronym=True, style=pypinyin.STYLE_NORMAL
            )
            if len(phonemes[0]) > 1 or phonemes[0][0] != y77_note.py:
                note.pronunciation = y77_note.py
            note_list.append(note)
        return note_list

    def parse_params(self, notes: list[Y77Note]) -> Params:
        params = Params()
        for y77_note in notes:
            if len(y77_note.pit):
                step = y77_note.len * 30 / (len(y77_note.pit) - 1)
                pbs = y77_note.pbs + 1
                params.pitch.points.append(Point(y77_note.start * 30 - 5 + 1920, -100))
                for i in range(len(y77_note.pit)):
                    params.pitch.points.append(
                        Point(
                            round(y77_note.start * 30 + i * step) + 1920,
                            round(
                                (
                                    (y77_note.pit[i] - 50) / 50 * pbs
                                    + 88
                                    - y77_note.pitch
                                )
                                * 100
                            ),
                        )
                    )
                params.pitch.points.append(
                    Point((y77_note.start + y77_note.len) * 30 + 5 + 1920, -100)
                )
        return params
