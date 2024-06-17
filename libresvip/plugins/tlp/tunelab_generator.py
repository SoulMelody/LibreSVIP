import dataclasses
import math

import more_itertools

from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.music_math import ratio_to_db

from .model import (
    TuneLabAudioPart,
    TuneLabMidiPart,
    TuneLabNote,
    TuneLabPoint,
    TuneLabPoints,
    TuneLabProject,
    TuneLabTempo,
    TuneLabTimeSignature,
    TuneLabTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class TuneLabGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> TuneLabProject:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        tempo_list = self.generate_tempos(project.song_tempo_list)
        time_signature_list = self.generate_time_signatures(project.time_signature_list)
        return TuneLabProject(
            tempos=tempo_list,
            time_signatures=time_signature_list,
            tracks=self.generate_tracks(project.track_list),
        )

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[TuneLabTempo]:
        song_tempo_list = skip_tempo_list(song_tempo_list, self.first_bar_length)
        return [
            TuneLabTempo(
                pos=tempo.position,
                bpm=tempo.bpm,
            )
            for tempo in song_tempo_list
        ]

    @staticmethod
    def generate_time_signatures(
        time_signature_list: list[TimeSignature],
    ) -> list[TuneLabTimeSignature]:
        return [
            TuneLabTimeSignature(
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
                bar_index=time_signature.bar_index,
            )
            for time_signature in time_signature_list
        ]

    def generate_tracks(self, track_list: list[Track]) -> list[TuneLabTrack]:
        tlp_track_list = []
        for track in track_list:
            if isinstance(track, InstrumentalTrack):
                if (track_info := audio_track_info(track.audio_file_path)) is not None:
                    tlp_track = TuneLabTrack(
                        name=track.title,
                        gain=self.generate_volume(track.volume),
                        pan=track.pan,
                        mute=track.mute,
                        solo=track.solo,
                        parts=[
                            TuneLabAudioPart(
                                name=track.title,
                                pos=track.offset,
                                path=track.audio_file_path,
                                dur=self.synchronizer.get_actual_ticks_from_secs_offset(
                                    track.offset, track_info.duration / 1000
                                ),
                            )
                        ],
                    )
                    tlp_track_list.append(tlp_track)
            elif isinstance(track, SingingTrack) and track.note_list:
                tlp_midi_part = TuneLabMidiPart(
                    name=track.title,
                    pos=0.0,
                    dur=math.ceil(track.note_list[-1].end_pos / self.first_bar_length)
                    * self.first_bar_length,
                    notes=self.generate_notes(track.note_list),
                )
                if pitch := self.generate_pitch(track.edited_params.pitch):
                    tlp_midi_part.pitch = pitch
                tlp_track = TuneLabTrack(
                    name=track.title,
                    gain=self.generate_volume(track.volume),
                    pan=track.pan,
                    mute=track.mute,
                    solo=track.solo,
                    parts=[tlp_midi_part],
                )
                tlp_track_list.append(tlp_track)
        return tlp_track_list

    @staticmethod
    def generate_volume(volume: float) -> float:
        return max(ratio_to_db(max(volume, 0.01)), -70) if volume > 0 else -70

    @staticmethod
    def generate_notes(note_list: list[Note]) -> list[TuneLabNote]:
        return [
            TuneLabNote(
                pos=note.start_pos,
                dur=note.length,
                pitch=note.key_number,
                lyric=note.lyric,
                pronunciation=note.pronunciation,
            )
            for note in note_list
        ]

    def generate_pitch(self, pitch: ParamCurve) -> list[TuneLabPoints]:
        return [
            TuneLabPoints(
                root=[
                    TuneLabPoint(
                        pos=point.x - self.first_bar_length,
                        value=point.y / 100,
                    )
                    for point in point_part
                ]
            )
            for point_part in more_itertools.split_at(
                pitch.points.root, lambda point: point.y == -100
            )
            if len(point_part)
        ]
