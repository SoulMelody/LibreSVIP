import dataclasses
import itertools

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .model import (
    VocaloidNotes,
    VocaloidPoint,
    VocaloidProject,
    VocaloidTimeSig,
    VocaloidTracks,
    VocaloidVoicePart,
    VocaloidWavPart,
)
from .options import InputOptions


@dataclasses.dataclass
class VocaloidParser:
    options: InputOptions
    comp_id2name: dict[str, str] = dataclasses.field(init=False)

    def parse_project(self, vpr_project: VocaloidProject) -> Project:
        self.comp_id2name = {voice.comp_id: voice.name for voice in vpr_project.voices}
        project = Project(
            TimeSignatureList=self.parse_time_signatures(
                vpr_project.master_track.time_sig.events
            ),
            SongTempoList=self.parse_tempos(vpr_project.master_track.tempo.events),
        )
        project.track_list = self.parse_tracks(vpr_project.tracks)
        return project

    def parse_time_signatures(
        self, time_signatures: list[VocaloidTimeSig]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                BarIndex=time_signature.bar,
                Numerator=time_signature.numer,
                Denominator=time_signature.denom,
            )
            for time_signature in time_signatures
        ]

    def parse_tempos(self, tempos: list[VocaloidPoint]) -> list[SongTempo]:
        return [
            SongTempo(
                Position=tempo.pos,
                BPM=tempo.value / 100,
            )
            for tempo in tempos
        ]

    def parse_tracks(self, tracks: list[VocaloidTracks]) -> list[Track]:
        track_list = []
        for part in itertools.chain.from_iterable(track.parts for track in tracks):
            if isinstance(part, VocaloidWavPart):
                # wav_path = f"Project/Audio/{part.name}"
                instrumental_track = InstrumentalTrack(
                    Title=part.name,
                    Offset=part.pos,
                    AudioFilePath=part.wav.original_name,
                )
                track_list.append(instrumental_track)
            elif isinstance(part, VocaloidVoicePart):
                comp_id = None
                if part.voice is not None:
                    comp_id = part.voice.comp_id
                elif part.ai_voice is not None:
                    comp_id = part.ai_voice.comp_id
                singing_track = SingingTrack(
                    Offset=part.pos,
                    NoteList=self.parse_notes(part.notes, part.pos),
                    AISingerName=self.comp_id2name.get(comp_id, ""),
                    # TODO: Add support for params
                )
                track_list.append(singing_track)
            else:
                part.pop("notes", None)
                print(f"Unknown part type: {part}")
        return track_list

    def parse_notes(self, notes: list[VocaloidNotes], pos: int) -> list[Note]:
        note_list = []
        for note in notes:
            note_list.append(
                Note(
                    StartPos=note.pos + pos,
                    Length=note.duration,
                    KeyNumber=note.number,
                    Lyric=note.lyric or note.phoneme,
                    # Pronunciation=note.phoneme,
                )
            )
        return note_list
