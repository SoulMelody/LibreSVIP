import dataclasses
import math

import pypinyin

from libresvip.core.exceptions import NoTrackError
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.portamento import PortamentoPitch
from libresvip.utils.translation import gettext_lazy as _

from .model import NNInfoLine, NNNote, NNPoints, NNProject, NNTimeSignature
from .options import OutputOptions


@dataclasses.dataclass
class NiaoniaoGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    length_multiplier: int = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    time_signatures: list[TimeSignature] = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> NNProject:
        self.length_multiplier = 60 if self.options.version == 19 else 30
        if self.options.track_index < 0:
            if (
                first_singing_track := next(
                    (
                        track
                        for track in project.track_list
                        if isinstance(track, SingingTrack) and track.note_list
                    ),
                    None,
                )
            ) is None:
                msg = _("No singing track found")
                raise NoTrackError(msg)
        else:
            first_singing_track = project.track_list[self.options.track_index]
        self.time_signatures = (
            project.time_signature_list[0]
            if len(project.time_signature_list)
            else [TimeSignature()]
        )
        nn_time_signature = self.generate_time_signature(project.time_signature_list)
        self.synchronizer = TimeSynchronizer(project.song_tempo_list, self.first_bar_length)
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
        pitch_simulator = None
        for note in singing_track.note_list:
            nn_note = NNNote(
                lyric=note.lyric,
                pronunciation=note.pronunciation or " ".join(pypinyin.lazy_pinyin(note.lyric)),
                key=83 - note.key_number,
                start=note.start_pos // self.length_multiplier,
                duration=note.length // self.length_multiplier,
            )
            if singing_track.edited_params.pitch:
                if pitch_simulator is None:
                    pitch_simulator = PitchSimulator(
                        synchronizer=self.synchronizer,
                        portamento=PortamentoPitch.no_portamento(),
                        note_list=singing_track.note_list,
                        time_signature_list=self.time_signatures,
                    )
                    pitch_simulator.merge_pitch_curve(
                        singing_track.edited_params.pitch, self.first_bar_length
                    )
                nn_note.pitch = self.generate_pitch(
                    pitch_simulator, note, nn_note.pitch_bend_sensitivity
                )
            nn_notes.append(nn_note)
        return nn_notes

    def generate_pitch(
        self, pitch_simulator: PitchSimulator, note: Note, pitch_bend_sensitivity: int
    ) -> NNPoints:
        nn_pitch_param = []
        for i in range(100):
            pitch_value = pitch_simulator.pitch_at_ticks(
                note.start_pos + int((note.length / 100.0) * i)
            )
            value = 50 + round((pitch_value - (note.key_number) * 100) / pitch_bend_sensitivity)
            nn_pitch_param.append(value)

        return NNPoints(points=nn_pitch_param)
