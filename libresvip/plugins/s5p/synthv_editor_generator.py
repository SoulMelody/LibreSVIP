import dataclasses

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Params,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils import ratio_to_db

from .model import (
    S5pInstrumental,
    S5pMeterItem,
    S5pMixer,
    S5pNote,
    S5pParameters,
    S5pPoint,
    S5pPoints,
    S5pProject,
    S5pTempoItem,
    S5pTrack,
    S5pTrackMixer,
)
from .options import OutputOptions

TICK_RATE = 1470000


@dataclasses.dataclass
class SynthVEditorGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> S5pProject:
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        s5p_project = S5pProject(
            tracks=self.generate_singing_tracks(project.track_list),
            tempo=self.generate_tempos(project.song_tempo_list),
            meter=self.generate_time_signatures(project.time_signature_list),
        )
        if (
            instrumental_track := next(
                (
                    S5pInstrumental(
                        filename=track.audio_file_path,
                        offset=self.synchronizer.get_actual_secs_from_ticks(
                            track.offset
                        ),
                    )
                    for track in project.track_list
                    if isinstance(track, InstrumentalTrack)
                ),
                None,
            )
        ) is not None:
            s5p_project.instrumental = self.generate_instrumental_track(
                instrumental_track
            )
            s5p_project.mixer = self.generate_mixer(instrumental_track)
        return s5p_project

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[S5pTempoItem]:
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return [
            S5pTempoItem(
                position=song_tempo.position * TICK_RATE,
                beat_per_minute=song_tempo.bpm,
            )
            for song_tempo in song_tempo_list
        ]

    @staticmethod
    def generate_time_signatures(
        time_signature_list: list[TimeSignature],
    ) -> list[S5pMeterItem]:
        return [
            S5pMeterItem(
                measure=time_signature.bar_index,
                beat_per_measure=time_signature.numerator,
                beat_granularity=time_signature.denominator,
            )
            for time_signature in time_signature_list
        ]

    @staticmethod
    def generate_volume(volume: float) -> float:
        return max(ratio_to_db(max(volume, 0.01)), -70) if volume > 0 else -70

    def generate_singing_tracks(self, track_list: list[Track]) -> list[S5pTrack]:
        tracks = []
        for i, track in enumerate(track_list):
            if isinstance(track, SingingTrack):
                track_mixer = S5pTrackMixer(
                    solo=track.solo,
                    muted=track.mute,
                    pan=track.pan,
                    gain_decibel=self.generate_volume(track.volume),
                )

                s5p_track = S5pTrack(
                    display_order=i,
                    name=track.title,
                    db_name=track.ai_singer_name,
                    notes=self.generate_notes(track.note_list),
                    mixer=track_mixer,
                )
                if track.edited_params is not None:
                    s5p_track.parameters = self.generate_parameters(
                        track.edited_params, track.note_list
                    )
                tracks.append(s5p_track)
        return tracks

    def generate_notes(self, note_list: list[Note]) -> list[S5pNote]:
        return [
            S5pNote(
                lyric=note.pronunciation or note.lyric,
                onset=note.start_pos * TICK_RATE,
                duration=note.length * TICK_RATE,
                pitch=note.key_number,
            )
            for note in note_list
        ]

    def generate_instrumental_track(self, track: InstrumentalTrack) -> S5pInstrumental:
        return S5pInstrumental(
            filename=track.audio_file_path,
            offset=self.synchronizer.get_actual_secs_from_ticks(track.offset),
        )

    def generate_mixer(self, track: InstrumentalTrack) -> S5pMixer:
        return S5pMixer(
            gain_instrumental_decibel=self.generate_volume(track.volume),
            instrumental_muted=track.mute,
        )

    def generate_parameters(
        self, edited_params: Params, note_list: list[Note]
    ) -> S5pParameters:
        interval = round(TICK_RATE * 3.75)
        rel_pitch_points = RelativePitchCurve(self.first_bar_length).from_absolute(
            edited_params.pitch, note_list
        )
        return S5pParameters(
            pitch_delta=self.generate_pitch_delta(rel_pitch_points, interval),
            interval=interval,
        )

    def generate_pitch_delta(self, pitch: Points, interval: int) -> S5pPoints:
        points = [
            S5pPoint(
                offset=round(point.x / (interval / TICK_RATE)),
                value=point.y,
            )
            for point in pitch or []
            if point.y != -100
        ]
        return S5pPoints(root=points)
