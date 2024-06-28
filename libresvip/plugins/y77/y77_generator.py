import dataclasses
from typing import Union

import pypinyin

from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
)

from .model import Y77Note, Y77Project
from .options import OutputOptions


@dataclasses.dataclass
class Y77Generator:
    options: OutputOptions
    first_bar_length: int = 0

    def generate_project(self, project: Project) -> Y77Project:
        if self.options.track_index < 0:
            first_singing_track = next(
                (track for track in project.track_list if isinstance(track, SingingTrack)),
                None,
            )
        else:
            first_singing_track = project.track_list[self.options.track_index]
            assert isinstance(first_singing_track, SingingTrack)
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        y77_project = Y77Project(
            bars=100,
            bpm=project.song_tempo_list[0].bpm,
            bbar=project.time_signature_list[0].numerator,
            bbeat=project.time_signature_list[0].denominator,
        )
        if first_singing_track is not None:
            y77_project.notes = self.generate_notes(first_singing_track)
            y77_project.nnote = len(y77_project.notes)
        return y77_project

    def generate_notes(self, singing_track: SingingTrack) -> list[Y77Note]:
        return [
            Y77Note(
                lyric=note.lyric,
                start=round(note.start_pos / 30),
                length=round(note.length / 30),
                pitch=88 - note.key_number,
                py=note.pronunciation or " ".join(pypinyin.lazy_pinyin(note.lyric)),
                pit=self.generate_pitch(singing_track.edited_params.pitch, note),
            )
            for note in singing_track.note_list
        ]

    def generate_pitch(self, pitch_param_curve: ParamCurve, note: Note) -> list[float]:
        sample_time_list = [
            note.start_pos + self.first_bar_length + int((note.length / 500.0) * i)
            for i in range(500)
        ]
        pitch_param_in_note = [
            p
            for p in pitch_param_curve.points.root
            if p.x >= note.start_pos + self.first_bar_length
            and p.x <= note.end_pos + self.first_bar_length
        ]

        pitch_param_time_in_note = dict(pitch_param_in_note)

        y77_pitch_param: list[Union[int, float]] = []
        for sample_time in sample_time_list:
            if (pitch := pitch_param_time_in_note.get(sample_time)) is None:
                distance = -1
                value = 50.0

                for point in pitch_param_in_note:
                    if distance > abs(point.x - sample_time) or distance == -1:
                        distance = abs(point.x - sample_time)
                        value = 50 + (
                            0 if point.y == -100 else (point.y - note.key_number * 100) / 2
                        )

                y77_pitch_param.append(value)

            elif pitch == -100:
                y77_pitch_param.append(50)
            else:
                y77_pitch_param.append(50 + (pitch - note.key_number * 100) / 2)
        buffer = []
        previous_node = y77_pitch_param[0]
        previous_node_index = 0
        for i in range(len(y77_pitch_param)):
            if y77_pitch_param[i] == previous_node:
                buffer.append(y77_pitch_param[i])
            else:
                for j in range(len(buffer)):
                    y77_pitch_param[previous_node_index + j] = previous_node + j * (
                        y77_pitch_param[i] - buffer[j]
                    ) / len(buffer)
                buffer.clear()

            if y77_pitch_param[i] != previous_node:
                previous_node_index = i
                previous_node = y77_pitch_param[i]

        return y77_pitch_param
