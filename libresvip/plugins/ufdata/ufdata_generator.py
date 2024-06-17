import dataclasses

from libresvip.core.tick_counter import skip_tempo_list
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
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> UFData:
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        return UFData(
            project=UFProject(
                tempos=self.generate_tempos(project.song_tempo_list),
                time_signatures=self.generate_time_signatures(project.time_signature_list),
                tracks=self.generate_tracks(project.track_list),
                measure_prefix=0,
            )
        )

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[UFTempos]:
        song_tempo_list = skip_tempo_list(song_tempo_list, self.first_bar_length)
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
                pitch=self.generate_pitch(track.edited_params.pitch, track.note_list),
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

    def generate_pitch(self, pitch: ParamCurve, notes: list[Note]) -> UFPitch:
        uf_pitch = UFPitch(
            is_absolute=True,
            ticks=[],
            values=[],
        )
        if notes:
            for point in pitch.points.root:
                if point.x not in (-192000, 1073741823):
                    uf_pitch.ticks.append(point.x - self.first_bar_length)
                    uf_pitch.values.append(0 if point.y == -100 else point.y / 100)
        return uf_pitch
