import dataclasses
import math

import pypinyin

from libresvip.core.exceptions import NoTrackError
from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils.translation import gettext_lazy as _

from .model import NNInfoLine, NNNote, NNPoints, NNProject, NNTimeSignature
from .options import OutputOptions


@dataclasses.dataclass
class NiaoniaoGenerator:
    options: OutputOptions
    length_multiplier: int = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> NNProject:
        self.length_multiplier = 60 if self.options.version == 19 else 30
        if self.options.track_index < 0:
            if (
                first_singing_track := next(
                    (track for track in project.track_list if isinstance(track, SingingTrack)),
                    None,
                )
            ) is None:
                msg = _("No singing track found")
                raise NoTrackError(msg)
        else:
            first_singing_track = project.track_list[self.options.track_index]
        nn_time_signature = self.generate_time_signature(project.time_signature_list)
        nn_tempo = self.generate_tempo(project.song_tempo_list)
        nn_info_line = NNInfoLine(
            version=self.options.version,
            time_signature=nn_time_signature,
            tempo=nn_tempo,
        )
        nn_project = NNProject(
            info_line=nn_info_line,
            notes=self.generate_notes(first_singing_track),
        )
        nn_project.note_count = len(nn_project.notes)
        if nn_project.note_count:
            nn_info_line.bar_count = math.ceil(
                (nn_project.notes[-1].start + nn_project.notes[-1].duration)
                * self.length_multiplier
                / self.first_bar_length
            )
        return nn_project

    def generate_time_signature(self, time_signature_list: list[TimeSignature]) -> NNTimeSignature:
        if not len(time_signature_list):
            self.first_bar_length = 1920
            return NNTimeSignature()
        self.first_bar_length = int(time_signature_list[0].bar_length())
        return NNTimeSignature(
            numerator=time_signature_list[0].numerator,
            denominator=time_signature_list[0].denominator,
        )

    def generate_tempo(self, tempo_list: list[SongTempo]) -> float:
        return tempo_list[0].bpm

    def generate_notes(self, singing_track: SingingTrack) -> list[NNNote]:
        nn_notes = []
        for note in singing_track.note_list:
            nn_note = NNNote(
                lyric=note.lyric,
                pronunciation=note.pronunciation or " ".join(pypinyin.lazy_pinyin(note.lyric)),
                key=88 - note.key_number,
                start=note.start_pos // self.length_multiplier,
                duration=note.length // self.length_multiplier,
            )
            if singing_track.edited_params.pitch:
                nn_note.pitch = self.generate_pitch(singing_track.edited_params.pitch, note)
            nn_notes.append(nn_note)
        return nn_notes

    def generate_pitch(self, pitch_param_curve: ParamCurve, note: Note) -> NNPoints:
        sample_time_list = [
            note.start_pos + self.first_bar_length + int((note.length / 100.0) * i)
            for i in range(100)
        ]
        pitch_param_in_note = [
            p
            for p in pitch_param_curve.points.root
            if p.x >= note.start_pos + self.first_bar_length
            and p.x < note.end_pos + self.first_bar_length
        ]

        pitch_param_time_in_note = dict(pitch_param_in_note)

        nn_pitch_param = []
        for sample_time in sample_time_list:
            if (pitch := pitch_param_time_in_note.get(sample_time)) is None:
                distance = -1
                value = 50

                for point in pitch_param_in_note:
                    if distance > abs(point.x - sample_time) or distance == -1:
                        distance = abs(point.x - sample_time)
                        value = 50 + (
                            0 if point.y == -100 else round((point.y - note.key_number * 100) / 12)
                        )

                nn_pitch_param.append(value)

            elif pitch == -100:
                nn_pitch_param.append(50)
            else:
                nn_pitch_param.append(50 + round((pitch - note.key_number * 100) / 12))
        buffer = []
        previous_node = nn_pitch_param[0]
        previous_node_index = 0
        for i in range(len(nn_pitch_param)):
            if nn_pitch_param[i] == previous_node:
                buffer.append(nn_pitch_param[i])
            else:
                for j in range(len(buffer)):
                    nn_pitch_param[previous_node_index + j] = round(
                        previous_node + j * (nn_pitch_param[i] - buffer[j]) / len(buffer)
                    )
                buffer.clear()

            if nn_pitch_param[i] != previous_node:
                previous_node_index = i
                previous_node = nn_pitch_param[i]

        return NNPoints(points=nn_pitch_param)
