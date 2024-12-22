import dataclasses

import more_itertools

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point
from libresvip.utils.music_math import hz2midi

from .model import (
    VoiceVoxNote,
    VoiceVoxProject,
    VoiceVoxTempo,
    VoiceVoxTimeSignature,
    VoiceVoxTrack,
)
from .options import InputOptions


@dataclasses.dataclass
class VOICEVOXParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, voicevox_project: VoiceVoxProject) -> Project:
        time_signatures = self.parse_time_signatures(voicevox_project.song.time_signatures)
        self.first_bar_length = int(time_signatures[0].bar_length(voicevox_project.song.tpqn))
        tempos = self.parse_tempos(voicevox_project.song.tempos)
        self.time_synchronizer = TimeSynchronizer(tempos)
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=[
                self.parse_track(voicevox_project.song.tracks[track_key])
                for track_key in voicevox_project.song.track_order
            ],
        )

    def parse_time_signatures(
        self, time_signatures: list[VoiceVoxTimeSignature]
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=time_signature.measure_number - 1,
                numerator=time_signature.beats,
                denominator=time_signature.beat_type,
            )
            for time_signature in time_signatures
        ]

    def parse_tempos(self, tempos: list[VoiceVoxTempo]) -> list[SongTempo]:
        return [SongTempo(bpm=tempo.bpm, position=tempo.position) for tempo in tempos]

    def parse_track(self, track: VoiceVoxTrack) -> SingingTrack:
        singing_track = SingingTrack(
            title=track.name,
            solo=track.solo,
            mute=track.mute,
            volume=track.gain,
            pan=track.pan,
            note_list=[self.parse_note(note) for note in track.notes],
        )
        if self.options.import_pitch:
            singing_track.edited_params.pitch.points.root = self.parse_pitch(track.pitch_edit_data)
        return singing_track

    def parse_note(self, note: VoiceVoxNote) -> Note:
        return Note(
            start_pos=note.position,
            length=note.duration,
            lyric=note.lyric,
            key_number=note.note_number,
        )

    def parse_pitch(self, pitch_edit_data: list[float]) -> list[Point]:
        secs = 0.0
        secs_step = 4 / 375
        points = [Point.start_point()]
        for part in more_itertools.split_when(
            pitch_edit_data,
            lambda x, y: [x, y].count(-1) == 1,
        ):
            if all(value == -1 for value in part):
                secs += secs_step * len(part)
            else:
                points.append(
                    Point(
                        int(self.time_synchronizer.get_actual_ticks_from_secs(secs))
                        + self.first_bar_length,
                        -100,
                    )
                )
                for value in part:
                    points.append(
                        Point(
                            int(self.time_synchronizer.get_actual_ticks_from_secs(secs))
                            + self.first_bar_length,
                            round(hz2midi(value) * 100),
                        )
                    )
                    secs += secs_step
                points.append(
                    Point(
                        int(self.time_synchronizer.get_actual_ticks_from_secs(secs))
                        + self.first_bar_length,
                        -100,
                    )
                )
        points.append(Point.end_point())
        return points
