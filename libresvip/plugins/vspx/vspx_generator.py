import dataclasses

from xsdata.formats.dataclass.models.generics import AnyElement

from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils import midi2note

from .model import (
    VocalSharpBeat,
    VocalSharpDefaultTrill,
    VocalSharpNote,
    VocalSharpNoteTrack,
    VocalSharpProject,
    VocalSharpSyllable,
    VocalSharpTempo,
)
from .options import OutputOptions


@dataclasses.dataclass
class VocalSharpGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> VocalSharpProject:
        vspx_project = VocalSharpProject()
        vspx_project.project.elements.extend(
            [
                AnyElement(qname="SamplesPerSec", text=44100),
                AnyElement(qname="Resolution", text=1920),
            ]
        )
        vspx_project.project.elements.append(VocalSharpDefaultTrill())
        vspx_project.project.elements.extend(
            self.generate_tempos(project.song_tempo_list)
        )
        vspx_project.project.elements.extend(
            self.generate_time_signatures(project.time_signature_list)
        )
        vspx_project.project.elements.extend(
            self.generate_singing_tracks(
                [
                    track
                    for track in project.track_list
                    if isinstance(track, SingingTrack)
                ]
            )
        )
        max_duration = max(
            (note.end_pos for track in project.track_list for note in track.note_list),
            default=0,
        )
        vspx_project.project.elements.insert(
            2, AnyElement(qname="Duration", text=max_duration)
        )
        return vspx_project

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[VocalSharpBeat]:
        return [
            VocalSharpBeat(
                bar_index=time_signature.bar_index,
                beat_per_bar=time_signature.numerator,
                bar_divide=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def generate_tempos(self, tempos: list[SongTempo]) -> list[VocalSharpTempo]:
        return [
            VocalSharpTempo(
                pos=tempo.position,
                bpm=tempo.bpm,
            )
            for tempo in tempos
        ]

    def generate_singing_tracks(
        self, singing_tracks: list[SingingTrack]
    ) -> list[VocalSharpNoteTrack]:
        note_tracks = []
        for track in singing_tracks:
            note_track = VocalSharpNoteTrack(
                name=track.title,
                singer=track.ai_singer_name,
                is_mute=str(track.mute),
                is_solo=str(track.solo),
                note=self.generate_notes(track.note_list),
            )
            note_tracks.append(note_track)
        return note_tracks

    def generate_notes(self, notes: list[Note]) -> list[VocalSharpNote]:
        return [
            VocalSharpNote(
                pos=note.start_pos,
                pitch=midi2note(note.key_number),
                duration=note.length,
                lyric=note.lyric or note.pronunciation,
                syllable=[VocalSharpSyllable()],
            )
            for note in notes
        ]
