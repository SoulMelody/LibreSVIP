import dataclasses

import more_itertools

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.point import Point

from .model import (
    TuneLabAudioPart,
    TuneLabMidiPart,
    TuneLabNote,
    TuneLabPoints,
    TuneLabProject,
    TuneLabTempo,
    TuneLabTimeSignature,
    TuneLabTrack,
)
from .options import InputOptions


@dataclasses.dataclass
class TuneLabParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)

    def parse_project(self, project: TuneLabProject) -> Project:
        time_signature_list = self.parse_time_signatures(project.time_signatures)
        self.first_bar_length = round(time_signature_list[0].bar_length())
        tempo_list = self.parse_tempos(project.tempos)
        return Project(
            song_tempo_list=tempo_list,
            time_signature_list=time_signature_list,
            track_list=self.parse_tracks(project.tracks),
        )

    def parse_time_signatures(
        self, time_signatures: list[TuneLabTimeSignature]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=time_signature.bar_index,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def parse_tempos(self, tempos: list[TuneLabTempo]) -> list[SongTempo]:
        return [SongTempo(position=int(tempo.pos), bpm=tempo.bpm) for tempo in tempos]

    def parse_tracks(self, tracks: list[TuneLabTrack]) -> list[Track]:
        track_list = []
        for track in tracks:
            for part in track.parts:
                if isinstance(part, TuneLabAudioPart) and self.options.import_instrumental_track:
                    track_list.append(
                        InstrumentalTrack(
                            audio_file_path=part.path,
                            title=part.name,
                            offset=int(part.pos),
                            volume=track.gain,
                            pan=track.pan,
                            mute=track.mute,
                            solo=track.solo,
                        )
                    )
                elif isinstance(part, TuneLabMidiPart) and len(part.notes):
                    singing_track = SingingTrack(
                        title=part.name,
                        volume=track.gain,
                        pan=track.pan,
                        mute=track.mute,
                        solo=track.solo,
                        note_list=self.parse_notes(part.notes, int(part.pos)),
                    )
                    if self.options.import_pitch and (
                        pitch_points := self.parse_pitch(part.pitch, int(part.pos))
                    ):
                        singing_track.edited_params.pitch.points.root = pitch_points
                    track_list.append(singing_track)
        return track_list

    @staticmethod
    def parse_notes(notes: list[TuneLabNote], offset: int) -> list[Note]:
        return [
            Note(
                start_pos=tlp_note.pos + offset,
                length=tlp_note.dur,
                key_number=tlp_note.pitch,
                lyric=tlp_note.lyric,
            )
            for tlp_note in notes
        ]

    def parse_pitch(self, pitch: list[TuneLabPoints], offset: int) -> list[Point]:
        points: list[Point] = []
        for pitch_part in pitch:
            for is_first, is_last, tlp_point in more_itertools.mark_ends(pitch_part.root):
                if is_first:
                    points.append(
                        Point(
                            x=tlp_point.pos + offset + self.first_bar_length,
                            y=-100,
                        )
                    )
                points.append(
                    Point(
                        x=tlp_point.pos + offset + self.first_bar_length,
                        y=round(tlp_point.value * 100),
                    )
                )
                if is_last:
                    points.append(
                        Point(
                            x=points[-1].x,
                            y=-100,
                        )
                    )
        return points
