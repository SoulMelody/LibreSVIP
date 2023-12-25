import dataclasses
import pathlib

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_CHINESE_LYRIC
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Params,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils import db_to_float, ratio_to_db

from .model import (
    S5pInstrumental,
    S5pMeterItem,
    S5pMixer,
    S5pNote,
    S5pParameters,
    S5pPoints,
    S5pProject,
    S5pTempoItem,
    S5pTrack,
)
from .options import InputOptions

TICK_RATE = 1470000


@dataclasses.dataclass
class SynthVEditorParser:
    options: InputOptions
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, s5p_project: S5pProject) -> Project:
        tempo_list = self.parse_tempos(s5p_project.tempo)
        time_signature_list = self.parse_time_signatures(s5p_project.meter)
        self.first_bar_length = round(time_signature_list[0].bar_length())
        track_list = self.parse_singing_tracks(s5p_project.tracks)
        self.synchronizer = TimeSynchronizer(tempo_list)
        if s5p_project.instrumental is not None:
            track_list.append(
                self.parse_instrumental_track(
                    s5p_project.instrumental, s5p_project.mixer
                )
            )
        return Project(
            time_signature_list=time_signature_list,
            song_tempo_list=tempo_list,
            track_list=track_list,
        )

    @staticmethod
    def parse_time_signatures(meter: list[S5pMeterItem]) -> list[TimeSignature]:
        time_signatures = [
            TimeSignature(
                bar_index=item.measure,
                numerator=item.beat_per_measure,
                denominator=item.beat_granularity,
            )
            for item in meter
        ]
        if not len(time_signatures):
            time_signatures.append(
                TimeSignature(bar_index=0, numerator=4, denominator=4)
            )
        return time_signatures

    @staticmethod
    def parse_tempos(tempo: list[S5pTempoItem]) -> list[SongTempo]:
        tempos = [
            SongTempo(
                position=item.position / TICK_RATE,
                bpm=item.beat_per_minute,
            )
            for item in tempo
        ]
        if not len(tempos):
            tempos.append(
                SongTempo(
                    position=0,
                    bpm=DEFAULT_BPM,
                )
            )
        return tempos

    def parse_singing_tracks(self, tracks: list[S5pTrack]) -> list[Track]:
        return [
            SingingTrack(
                mute=track.mixer.muted,
                solo=track.mixer.solo,
                volume=self.parse_volume(track.mixer.gain_decibel),
                pan=track.mixer.pan,
                ai_singer_name=track.db_name or "",
                title=track.name or f"Track {i + 1}",
                note_list=note_list,
                edited_params=self.parse_params(track.parameters, note_list),
            )
            for i, track in enumerate(tracks)
            if (note_list := self.parse_notes(track.notes))
        ]

    @staticmethod
    def parse_volume(gain: float) -> float:
        if gain >= 0:
            return min(gain / (ratio_to_db(4)) + 1.0, 2.0)
        else:
            return db_to_float(gain)

    def parse_instrumental_track(
        self, track: S5pInstrumental, mixer: S5pMixer
    ) -> InstrumentalTrack:
        return InstrumentalTrack(
            mute=mixer.instrumental_muted,
            volume=self.parse_volume(mixer.gain_instrumental_decibel),
            title=pathlib.Path(track.filename).name,
            audio_file_path=track.filename,
            offset=round(self.synchronizer.get_actual_ticks_from_secs(track.offset)),
        )

    def parse_notes(self, notes: list[S5pNote]) -> list[Note]:
        return [
            Note(
                key_number=s5p_note.pitch,
                start_pos=round(s5p_note.onset / TICK_RATE),
                length=round(s5p_note.duration / TICK_RATE),
                lyric=s5p_note.lyric.replace(" ", "") or DEFAULT_CHINESE_LYRIC,
            )
            for s5p_note in notes
        ]

    def parse_params(self, parameters: S5pParameters, note_list: list[Note]) -> Params:
        rel_pitch_points = self.parse_pitch_curve(
            parameters.pitch_delta, parameters.interval
        )
        return Params(
            pitch=RelativePitchCurve(self.first_bar_length).to_absolute(
                rel_pitch_points, note_list
            ),
        )

    @staticmethod
    def parse_pitch_curve(pitch_delta: S5pPoints, interval: int) -> Points:
        return Points(
            root=[
                Point(
                    x=round(point.offset * (interval / TICK_RATE)),
                    y=round(point.value),
                )
                for point in pitch_delta
            ]
        )
