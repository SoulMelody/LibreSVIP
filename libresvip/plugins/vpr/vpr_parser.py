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
            time_signature_list=self.parse_time_signatures(
                vpr_project.master_track.time_sig.events
            ),
            song_tempo_list=self.parse_tempos(vpr_project.master_track.tempo.events),
        )
        project.track_list = self.parse_tracks(vpr_project.tracks)
        return project

    def parse_time_signatures(
        self, time_signatures: list[VocaloidTimeSig]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=time_signature.bar,
                numerator=time_signature.numer,
                denominator=time_signature.denom,
            )
            for time_signature in time_signatures
        ]

    def parse_tempos(self, tempos: list[VocaloidPoint]) -> list[SongTempo]:
        return [
            SongTempo(
                position=tempo.pos,
                bpm=tempo.value / 100,
            )
            for tempo in tempos
        ]

    def parse_tracks(self, tracks: list[VocaloidTracks]) -> list[Track]:
        track_list = []
        for part in itertools.chain.from_iterable(track.parts for track in tracks):
            if isinstance(part, VocaloidWavPart):
                # wav_path = f"Project/Audio/{part.name}"
                instrumental_track = InstrumentalTrack(
                    title=part.name,
                    offset=part.pos,
                    audio_file_path=part.wav.original_name,
                )
                track_list.append(instrumental_track)
            elif isinstance(part, VocaloidVoicePart):
                comp_id = None
                if part.voice is not None:
                    comp_id = part.voice.comp_id
                elif part.ai_voice is not None:
                    comp_id = part.ai_voice.comp_id
                singing_track = SingingTrack(
                    offset=part.pos,
                    note_list=self.parse_notes(part.notes, part.pos),
                    ai_singer_name=self.comp_id2name.get(comp_id, ""),
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
                    start_pos=note.pos + pos,
                    length=note.duration,
                    key_number=note.number,
                    lyric=note.lyric or note.phoneme,
                    # pronunciation=note.phoneme,
                )
            )
        return note_list
