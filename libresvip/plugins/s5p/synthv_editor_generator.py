import dataclasses
from typing import List

from pydub.utils import ratio_to_db

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

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
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> S5pProject:
        s5p_project = S5pProject(
            tracks=self.generate_singing_tracks(project.track_list),
            tempo=self.generate_tempos(project.song_tempo_list),
            meter=self.generate_time_signatures(project.time_signature_list),
        )
        instrumental_track = self.generate_instrumental_track(project.track_list)
        if instrumental_track is not None:
            s5p_project.instrumental = instrumental_track
            s5p_project.mixer = self.generate_mixer(project.track_list)
        return s5p_project

    def generate_tempos(self, song_tempo_list: List[SongTempo]) -> List[S5pTempoItem]:
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return [
            S5pTempoItem(
                position=song_tempo.position * TICK_RATE,
                beatPerMinute=song_tempo.bpm,
            )
            for song_tempo in song_tempo_list
        ]

    @staticmethod
    def generate_time_signatures(
        time_signature_list: List[TimeSignature],
    ) -> List[S5pMeterItem]:
        return [
            S5pMeterItem(
                measure=time_signature.bar_index,
                beatPerMeasure=time_signature.numerator,
                beatGranularity=time_signature.denominator,
            )
            for time_signature in time_signature_list
        ]

    @staticmethod
    def generate_volume(volume: float) -> float:
        return max(ratio_to_db(max(volume, 0.01)), -70) if volume > 0 else -70

    def generate_singing_tracks(self, track_list: List[Track]) -> List[S5pTrack]:
        tracks = []
        for i, track in enumerate(track_list):
            if isinstance(track, SingingTrack):
                track_mixer = S5pTrackMixer(
                    solo=track.solo,
                    muted=track.mute,
                    pan=track.pan,
                    gainDecibel=self.generate_volume(track.volume),
                )

                s5p_track = S5pTrack(
                    displayOrder=i,
                    name=track.title,
                    dbName=track.ai_singer_name,
                    notes=self.generate_notes(track.note_list),
                    mixer=track_mixer,
                )
                if track.edited_params is not None:
                    s5p_track.parameters = self.generate_parameters(track.edited_params)
                tracks.append(s5p_track)
        return tracks

    def generate_notes(self, note_list: List[Note]) -> List[S5pNote]:
        return [
            S5pNote(
                lyric=note.pronunciation or note.lyric,
                onset=note.start_pos * TICK_RATE,
                duration=note.length * TICK_RATE,
                pitch=note.key_number,
            )
            for note in note_list
        ]

    def generate_instrumental_track(self, track_list: List[Track]) -> S5pInstrumental:
        return next(
            (
                S5pInstrumental(
                    filename=track.audio_file_path,
                    offset=track.offset,
                )
                for track in track_list
                if isinstance(track, InstrumentalTrack)
            ),
            None,
        )

    def generate_mixer(self, track_list: List[Track]) -> S5pMixer:
        return next(
            (
                S5pMixer(
                    gainInstrumentalDecibel=self.generate_volume(track.volume),
                    instrumentalMuted=track.mute,
                )
                for track in track_list
                if isinstance(track, InstrumentalTrack)
            ),
            None,
        )

    def generate_parameters(self, edited_params: Params) -> S5pParameters:
        interval = round(TICK_RATE * 3.75)
        return S5pParameters(
            pitchDelta=self.generate_pitch_delta(edited_params.pitch, interval),
            interval=interval,
        )

    def generate_pitch_delta(self, pitch: ParamCurve, interval: int) -> S5pPoints:
        points = [
            S5pPoint(
                offset=round(point.x / (interval / TICK_RATE)),
                value=point.y * 100,
            )
            for point in pitch.points
        ]
        return S5pPoints(root=points)
