import dataclasses

from libresvip.core.tick_counter import skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.music_math import ratio_to_db

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
            tempo=self.generate_tempos(project.song_tempo_list),
            meter=self.generate_time_signatures(project.time_signature_list),
            tracks=self.generate_singing_tracks(project.track_list),
        )
        if (
            instrumental_track_and_mixer := next(
                (
                    self.generate_instrumental_track_and_mixer(track)
                    for track in project.track_list
                    if isinstance(track, InstrumentalTrack)
                ),
                None,
            )
        ) is not None:
            s5p_project.instrumental, s5p_project.mixer = instrumental_track_and_mixer
        return s5p_project

    def generate_tempos(self, song_tempo_list: list[SongTempo]) -> list[S5pTempoItem]:
        song_tempo_list = skip_tempo_list(song_tempo_list, self.first_bar_length)
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
        if not tracks:
            tracks.append(
                S5pTrack(
                    name="Unnamed Track",
                    notes=[None],
                )
            )
        return tracks

    def generate_notes(self, note_list: list[Note]) -> list[S5pNote]:
        return [
            S5pNote(
                lyric=note.lyric,
                onset=note.start_pos * TICK_RATE,
                duration=note.length * TICK_RATE,
                pitch=note.key_number,
                d_f0_vbr=0,
            )
            for note in note_list
        ]

    def generate_instrumental_track_and_mixer(
        self, track: InstrumentalTrack
    ) -> tuple[S5pInstrumental, S5pMixer]:
        return S5pInstrumental(
            filename=track.audio_file_path,
            offset=self.synchronizer.get_actual_secs_from_ticks(track.offset),
        ), S5pMixer(
            gain_instrumental_decibel=self.generate_volume(track.volume),
            instrumental_muted=track.mute,
        )

    def generate_parameters(self, edited_params: Params, note_list: list[Note]) -> S5pParameters:
        interval = round(TICK_RATE * 3.75)
        pitch_simulator = PitchSimulator(
            synchronizer=self.synchronizer,
            portamento=PortamentoPitch.sigmoid_portamento(),
            note_list=note_list,
        )
        rel_pitch_points = RelativePitchCurve(self.first_bar_length).from_absolute(
            edited_params.pitch.points.root, pitch_simulator
        )
        return S5pParameters(
            pitch_delta=self.generate_pitch_delta(rel_pitch_points, interval),
            interval=interval,
        )

    def generate_pitch_delta(self, pitch: list[Point], interval: int) -> S5pPoints:
        return S5pPoints(
            root=[
                S5pPoint(
                    offset=round(point.x / (interval / TICK_RATE)),
                    value=point.y,
                )
                for point in pitch
                if point.y != -100
            ]
        )
