import dataclasses

from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .model import (
    UFData,
    UFNotes,
    UFPitch,
    UFProject,
    UFTempos,
    UFTimeSignatures,
    UFTracks,
)
from .options import OutputOptions


@dataclasses.dataclass
class UFDataGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> UFData:
        return UFData(
            project=UFProject(
                tempos=self.generate_tempos(project.song_tempo_list),
                time_signatures=self.generate_time_signatures(
                    project.time_signature_list
                ),
                tracks=self.generate_tracks(project.track_list),
                measure_prefix=0,
            )
        )

    @staticmethod
    def generate_tempos(song_tempo_list: list[SongTempo]) -> list[UFTempos]:
        return [
            UFTempos(
                tick_position=tempo.position,
                bpm=tempo.bpm,
            )
            for tempo in song_tempo_list
        ]

    @staticmethod
    def generate_time_signatures(
        time_signature_list: list[TimeSignature],
    ) -> list[UFTimeSignatures]:
        return [
            UFTimeSignatures(
                measure_position=time_signature.bar_index,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            for time_signature in time_signature_list
        ]

    def generate_tracks(self, track_list: list[Track]) -> list[UFTracks]:
        return [
            UFTracks(
                name=track.title,
                notes=self.generate_notes(track.note_list),
                pitch=self.generate_pitch(track.edited_params.pitch),
            )
            for track in track_list
            if isinstance(track, SingingTrack)
        ]

    @staticmethod
    def generate_notes(note_list: list[Note]) -> list[UFNotes]:
        return [
            UFNotes(
                tick_on=note.start_pos,
                tick_off=note.end_pos,
                lyric=note.lyric,
                key=note.key_number,
            )
            for note in note_list
        ]

    @staticmethod
    def generate_pitch(pitch: ParamCurve) -> UFPitch:
        return UFPitch(
            is_absolute=True,
            ticks=[point.x for point in pitch.points],
            values=[point.y for point in pitch.points],
        )
