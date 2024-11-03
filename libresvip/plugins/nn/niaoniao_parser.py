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

from .model import NNInfoLine, NNNote, NNProject, NNTimeSignature
from .options import InputOptions


@dataclasses.dataclass
class NiaoNiaoParser:
    options: InputOptions
    length_multiplier: int = dataclasses.field(init=False)

    def parse_project(self, nn_project: NNProject) -> Project:
        self.length_multiplier = 60 if nn_project.info_line.version == 19 else 30
        return Project(
            song_tempo_list=self.parse_tempos(nn_project.info_line),
            time_signature_list=self.parse_time_signatures(nn_project.info_line.time_signature),
            track_list=self.parse_tracks(nn_project.notes),
        )

    def parse_tempos(self, info_line: NNInfoLine) -> list[SongTempo]:
        return [SongTempo(bpm=info_line.tempo, position=0)]

    def parse_time_signatures(self, time_signature: NNTimeSignature) -> list[TimeSignature]:
        return [
            TimeSignature(
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
        ]

    def parse_tracks(self, notes: list[NNNote]) -> list[SingingTrack]:
        return [
            SingingTrack(
                note_list=self.parse_notes(notes),
                edited_params=self.parse_params(notes),
            )
        ]

    def parse_notes(self, notes: list[NNNote]) -> list[Note]:
        note_list = []
        for nn_note in notes:
            note = Note(
                lyric=nn_note.lyric,
                start_pos=nn_note.start * self.length_multiplier,
                length=nn_note.duration * self.length_multiplier,
                key_number=88 - nn_note.key,
            )
            phonemes = pypinyin.pinyin(nn_note.lyric, heteronym=True, style=pypinyin.STYLE_NORMAL)
            if len(phonemes[0]) > 1 or phonemes[0][0] != nn_note.pronunciation:
                note.pronunciation = nn_note.pronunciation
            note_list.append(note)
        return note_list

    def parse_params(self, notes: list[NNNote]) -> Params:
        params = Params()
        for nn_note in notes:
            if (
                self.options.import_pitch
                and nn_note.pitch.point_count > 0
                and any(point != 50 for point in nn_note.pitch.points)
            ):
                step = nn_note.duration * self.length_multiplier / (nn_note.pitch.point_count - 1)
                pbs = nn_note.pitch_bend_sensitivity + 1
                params.pitch.points.append(
                    Point(nn_note.start * self.length_multiplier - 5 + 1920, -100)
                )
                for i in range(nn_note.pitch.point_count):
                    params.pitch.points.append(
                        Point(
                            round(nn_note.start * self.length_multiplier + i * step) + 1920,
                            round(
                                ((nn_note.pitch.points[i] - 50) / 50 * pbs + 88 - nn_note.key) * 100
                            ),
                        )
                    )
                params.pitch.points.append(
                    Point(
                        (nn_note.start + nn_note.duration) * self.length_multiplier + 5 + 1920,
                        -100,
                    )
                )
            # TODO: volume
        return params
