import dataclasses
import os

from pydub.utils import db_to_float, ratio_to_db

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_CHINESE_LYRIC
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Point,
    Points,
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
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, s5p_project: S5pProject) -> Project:
        track_list = self.parse_singing_tracks(s5p_project.tracks)
        tempo_list = self.parse_tempos(s5p_project.tempo)
        self.synchronizer = TimeSynchronizer(tempo_list)
        if s5p_project.instrumental is not None:
            track_list.append(
                self.parse_instrumental_track(
                    s5p_project.instrumental, s5p_project.mixer
                )
            )
        return Project(
            time_signature_list=self.parse_time_signatures(s5p_project.meter),
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
                note_list=self.parse_notes(track.notes),
                edited_params=self.parse_params(track.parameters),
            )
            for i, track in enumerate(tracks)
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
            title=os.path.basename(track.filename),
            audio_file_path=track.filename,
            offset=round(self.synchronizer.get_actual_ticks_from_secs(track.offset)),
        )

    def parse_notes(self, notes: list[S5pNote]) -> list[Note]:
        note_list = []
        for s5p_note in notes:
            note = Note(
                key_number=s5p_note.pitch,
                start_pos=round(s5p_note.onset / TICK_RATE),
                length=round(s5p_note.duration / TICK_RATE),
                lyric=s5p_note.lyric.replace(" ", "") or DEFAULT_CHINESE_LYRIC,
            )
            note_list.append(note)
        return note_list

    def parse_params(self, parameters: S5pParameters) -> Params:
        return Params(
            pitch=self.parse_pitch_curve(parameters.pitch_delta, parameters.interval),
        )

    @staticmethod
    def parse_pitch_curve(pitch_delta: S5pPoints, interval: int) -> ParamCurve:
        return ParamCurve(
            points=Points(
                root=[
                    Point(
                        x=round(point.offset * (interval / TICK_RATE)),
                        y=round(point.value / 100),
                    )
                    for point in pitch_delta
                ]
            ),
        )
