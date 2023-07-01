import dataclasses
import os

from pydub.utils import db_to_float, ratio_to_db

from libresvip.core.constants import DEFAULT_BPM, DEFAULT_LYRIC
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
            TimeSignatureList=self.parse_time_signatures(s5p_project.meter),
            SongTempoList=tempo_list,
            TrackList=track_list,
        )

    @staticmethod
    def parse_time_signatures(meter: list[S5pMeterItem]) -> list[TimeSignature]:
        time_signatures = [
            TimeSignature(
                BarIndex=item.measure,
                Numerator=item.beat_per_measure,
                Denominator=item.beat_granularity,
            )
            for item in meter
        ]
        if not len(time_signatures):
            time_signatures.append(
                TimeSignature(BarIndex=0, Numerator=4, Denominator=4)
            )
        return time_signatures

    @staticmethod
    def parse_tempos(tempo: list[S5pTempoItem]) -> list[SongTempo]:
        tempos = [
            SongTempo(
                Position=item.position / TICK_RATE,
                BPM=item.beat_per_minute,
            )
            for item in tempo
        ]
        if not len(tempos):
            tempos.append(
                SongTempo(
                    Position=0,
                    BPM=DEFAULT_BPM,
                )
            )
        return tempos

    def parse_singing_tracks(self, tracks: list[S5pTrack]) -> list[Track]:
        return [
            SingingTrack(
                Mute=track.mixer.muted,
                Solo=track.mixer.solo,
                Volume=self.parse_volume(track.mixer.gain_decibel),
                Pan=track.mixer.pan,
                AISingerName=track.db_name or "",
                Title=track.name or f"Track {i + 1}",
                NoteList=self.parse_notes(track.notes),
                EditedParams=self.parse_params(track.parameters),
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
            Mute=mixer.instrumental_muted,
            Volume=self.parse_volume(mixer.gain_instrumental_decibel),
            Title=os.path.basename(track.filename),
            AudioFilePath=track.filename,
            Offset=round(self.synchronizer.get_actual_ticks_from_secs(track.offset)),
        )

    def parse_notes(self, notes: list[S5pNote]) -> list[Note]:
        note_list = []
        for s5p_note in notes:
            note = Note(
                KeyNumber=s5p_note.pitch,
                StartPos=round(s5p_note.onset / TICK_RATE),
                Length=round(s5p_note.duration / TICK_RATE),
                Lyric=s5p_note.lyric.replace(" ", "") or DEFAULT_LYRIC,
            )
            note_list.append(note)
        return note_list

    def parse_params(self, parameters: S5pParameters) -> Params:
        return Params(
            Pitch=self.parse_pitch_curve(parameters.pitch_delta, parameters.interval),
        )

    @staticmethod
    def parse_pitch_curve(pitch_delta: S5pPoints, interval: int) -> ParamCurve:
        return ParamCurve(
            PointList=Points(
                root=[
                    Point(
                        x=round(point.offset * (interval / TICK_RATE)),
                        y=round(point.value / 100),
                    )
                    for point in pitch_delta
                ]
            ),
        )
