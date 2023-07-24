import dataclasses

from construct_typed import DataclassMixin, DataclassStruct

from libresvip.core.tick_counter import shift_beat_list, shift_tempo_list
from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature

from .model import (
    DvInnerProject,
    DvNote,
    DvNoteParameter,
    DvProject,
    DvSegment,
    DvSingingTrack,
    DvTempo,
    DvTimeSignature,
    DvTrack,
    DvTrackType,
)
from .options import OutputOptions


def size_of_object(obj: DataclassMixin) -> int:
    return len(DataclassStruct(type(obj)).build(obj))


@dataclasses.dataclass
class DeepVocalGenerator:
    options: OutputOptions
    tick_prefix: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> DvProject:
        self.tick_prefix = round(4 * project.time_signature_list[0].bar_length())
        singing_tracks = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)]
        )
        return DvProject(
            inner_project=DvInnerProject(
                tracks=singing_tracks,
                tempos=self.generate_tempos(project.song_tempo_list),
                time_signatures=self.generate_time_signatures(
                    project.time_signature_list
                ),
            )
        )

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[DvTimeSignature]:
        return shift_beat_list(
            [
                DvTimeSignature(
                    measure_position=ts.bar_index,
                    numerator=ts.numerator,
                    denominator=ts.denominator,
                )
                for ts in time_signatures
            ],
            -4,
        )

    def generate_tempos(self, tempos: list[SongTempo]) -> list[DvTempo]:
        return shift_tempo_list(
            [
                DvTempo(position=tempo.position, bpm=round(tempo.bpm * 100))
                for tempo in tempos
            ],
            -self.tick_prefix,
        )

    def generate_singing_tracks(
        self, singing_tracks: list[SingingTrack]
    ) -> list[DvTrack]:
        track_list = []
        for track in singing_tracks:
            dv_notes = self.generate_notes(track.note_list)
            dv_segment = DvSegment(
                start=self.tick_prefix,
                name=track.title,
                singer_name=track.ai_singer_name,
                length=max(note.end_pos for note in track.note_list),
                notes=dv_notes,
                volume_data=[],
                pitch_data=[],
                unknown_1=[],
                breath_data=[],
                gender_data=[],
                unknown_2=[],
                unknown_3=[],
            )
            dv_track = DvSingingTrack(
                name=track.title,
                mute=track.mute,
                solo=track.solo,
                volume=30,
                balance=0,
                segments=[dv_segment],
            )
            track_list.append(
                DvTrack(
                    track_type=DvTrackType.SINGING,
                    track_data=dv_track,
                )
            )
        return track_list

    def generate_notes(self, notes: list[Note]) -> list[DvNote]:
        return [
            DvNote(
                start=note.start_pos - self.tick_prefix,
                length=note.length,
                key=note.key_number,
                phoneme=note.pronunciation or "",
                word=note.lyric,
                padding_1=0,
                vibrato=50,
                note_vibrato_data=DvNoteParameter(
                    amplitude_points=[],
                    frequency_points=[],
                    vibrato_points=[],
                ),
                unknown_phonemes=b"\x00\x00\x00\x80?\x00\x00\x00\x80?\x00\x00\x80?\x00\x00\x80?",
                ben_depth=8,
                ben_length=5,
                por_head=16,
                por_tail=16,
                timbre=-1,
                cross_lyric="",
                cross_timbre=-1,
            )
            for note in notes
        ]
