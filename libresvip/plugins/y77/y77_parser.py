import dataclasses

import pypinyin

from libresvip.model.base import (
    Note,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point

from .model import Y77Note, Y77Project
from .options import InputOptions


@dataclasses.dataclass
class Y77Parser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, y77_project: Y77Project) -> Project:
        time_signatures = self.parse_time_signatures(y77_project)
        self.first_bar_length = round(time_signatures[0].bar_length())
        return Project(
            song_tempo_list=self.parse_tempos(y77_project.bpm),
            time_signature_list=time_signatures,
            track_list=self.parse_tracks(y77_project.notes),
        )

    def parse_tempos(self, bpm: float) -> list[SongTempo]:
        return [SongTempo(bpm=bpm, position=0)]

    def parse_time_signatures(self, y77_project: Y77Project) -> list[TimeSignature]:
        return [
            TimeSignature(
                numerator=y77_project.bbar,
                denominator=y77_project.bbeat,
            )
        ]

    def parse_tracks(self, notes: list[Y77Note]) -> list[SingingTrack]:
        return [
            SingingTrack(
                ai_singer_name="元七七",
                note_list=self.parse_notes(notes),
                edited_params=self.parse_params(notes),
            )
        ]

    def parse_notes(self, notes: list[Y77Note]) -> list[Note]:
        note_list = []
        for y77_note in notes:
            note = Note(
                lyric=y77_note.lyric,
                start_pos=y77_note.start * 30,
                length=y77_note.length * 30,
                key_number=88 - y77_note.pitch,
            )
            phonemes = pypinyin.pinyin(y77_note.lyric, heteronym=True, style=pypinyin.STYLE_NORMAL)
            if len(phonemes[0]) > 1 or phonemes[0][0] != y77_note.py:
                note.pronunciation = y77_note.py
            note_list.append(note)
        return note_list

    def parse_params(self, notes: list[Y77Note]) -> Params:
        params = Params()
        for y77_note in notes:
            if self.options.import_pitch and len(y77_note.pit):
                step = y77_note.length * 30 / (len(y77_note.pit) - 1)
                pbs = y77_note.pbs + 1
                params.pitch.points.append(
                    Point(y77_note.start * 30 - 5 + self.first_bar_length, -100)
                )
                for i in range(len(y77_note.pit)):
                    params.pitch.points.append(
                        Point(
                            round(y77_note.start * 30 + i * step) + self.first_bar_length,
                            round(((y77_note.pit[i] - 50) / 50 * pbs + 88 - y77_note.pitch) * 100),
                        )
                    )
                params.pitch.points.append(
                    Point(
                        (y77_note.start + y77_note.length) * 30 + 5 + self.first_bar_length,
                        -100,
                    )
                )
        return params
