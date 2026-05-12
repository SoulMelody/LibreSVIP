import dataclasses
import operator

import more_itertools

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
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
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.audio import audio_track_info
from libresvip.utils.text import uuid_str

from .model import (
    MikotoStudioSequenceFormat,
    MsqAudio,
    MsqAudioClip,
    MsqAudioTrack,
    MsqBpmEvent,
    MsqColor,
    MsqMainOut,
    MsqMixer,
    MsqNote,
    MsqParameter,
    MsqParameters,
    MsqPoint,
    MsqSetup,
    MsqSinger,
    MsqSingerClip,
    MsqSingerInstrument,
    MsqSingerTrack,
    MsqTimeSignature,
    MsqTimeSignatureEvent,
    MsqTrack,
)
from .options import OutputOptions


@dataclasses.dataclass
class MsqGenerator:
    options: OutputOptions
    ppq: float = TICKS_IN_BEAT
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    time_signatures: list[TimeSignature] = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> MikotoStudioSequenceFormat:
        song_tempo_list = project.song_tempo_list or [SongTempo(bpm=DEFAULT_BPM)]
        self.time_signatures = project.time_signature_list or [TimeSignature()]
        self.first_bar_length = round(self.time_signatures[0].bar_length())
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        out_id = uuid_str()
        tracks: list[MsqTrack] = []
        for index, track in enumerate(project.track_list):
            if isinstance(track, SingingTrack):
                tracks.append(self.generate_singing_track(track, index, out_id))
            elif isinstance(track, InstrumentalTrack):
                tracks.append(self.generate_instrumental_track(track, index, out_id))
        setup = MsqSetup(
            ppq=self.ppq,
            bpm=song_tempo_list[0].bpm,
            time_signature=MsqTimeSignature(
                numerator=self.time_signatures[0].numerator,
                denominator=self.time_signatures[0].denominator,
            ),
            bpm_events=self.generate_bpm_events(song_tempo_list),
            time_signature_events=self.generate_time_signature_events(self.time_signatures),
        )
        return MikotoStudioSequenceFormat(
            setup=setup,
            main_out=MsqMainOut(id=out_id, name="Main Out"),
            aux=[],
            tracks=tracks,
        )

    def to_msq_ticks(self, value: int) -> int:
        return round(value * self.ppq / TICKS_IN_BEAT)

    def to_relative_msq_ticks(self, clip_start: int, value: int) -> int:
        return self.to_msq_ticks(value - clip_start)

    def generate_bpm_events(self, tempos: list[SongTempo]) -> list[MsqBpmEvent]:
        tempo_events = sorted(tempos, key=operator.attrgetter("position"))
        if not tempo_events or tempo_events[0].position > 0:
            tempo_events = [
                SongTempo(position=0, bpm=tempo_events[0].bpm if tempo_events else DEFAULT_BPM),
                *tempo_events,
            ]
        return [
            MsqBpmEvent(
                position=self.to_msq_ticks(tempo.position),
                bpm=tempo.bpm,
            )
            for tempo in tempo_events
        ]

    def generate_time_signature_events(
        self,
        time_signatures: list[TimeSignature],
    ) -> list[MsqTimeSignatureEvent]:
        sorted_time_signatures = sorted(
            time_signatures,
            key=operator.attrgetter("bar_index"),
        )
        if not sorted_time_signatures:
            sorted_time_signatures = [TimeSignature()]
        events: list[MsqTimeSignatureEvent] = []
        position = 0.0
        prev_time_signature = sorted_time_signatures[0]
        events.append(
            MsqTimeSignatureEvent(
                position=0,
                time_sig=MsqTimeSignature(
                    numerator=prev_time_signature.numerator,
                    denominator=prev_time_signature.denominator,
                ),
            )
        )
        for time_signature in sorted_time_signatures[1:]:
            position += (
                (time_signature.bar_index - prev_time_signature.bar_index)
                * self.ppq
                * 4
                * prev_time_signature.numerator
                / prev_time_signature.denominator
            )
            events.append(
                MsqTimeSignatureEvent(
                    position=round(position),
                    time_sig=MsqTimeSignature(
                        numerator=time_signature.numerator,
                        denominator=time_signature.denominator,
                    ),
                )
            )
            prev_time_signature = time_signature
        return events

    def generate_singing_track(
        self, track: SingingTrack, index: int, out_id: str
    ) -> MsqSingerTrack:
        track_id = uuid_str()
        singer_id = f"usid:{uuid_str()[4:23]}"
        return MsqSingerTrack(
            id=track_id,
            mixer=MsqMixer(
                gain=track.volume,
                pan=track.pan,
                record_arm=False,
                solo=track.solo,
                mute=track.mute,
                output=out_id,
            ),
            name=track.title,
            color="orange",
            index=index,
            track_type="Singer",
            instrument=MsqSingerInstrument(
                singer=MsqSinger(
                    name=track.ai_singer_name or "Singer",
                    id=singer_id,
                )
            ),
            clips=self.generate_singing_clips(track, track_id),
        )

    def generate_singing_clips(self, track: SingingTrack, track_id: str) -> list[MsqSingerClip]:
        if not track.note_list:
            return []
        clip_id = uuid_str()
        notes = sorted(track.note_list, key=operator.attrgetter("start_pos"))
        clip_start = self.get_clip_start(track.edited_params, notes)
        clip_end = self.get_clip_end(track.edited_params, notes)
        msq_notes = [self.generate_note(note, clip_id, clip_start) for note in notes]
        return [
            MsqSingerClip(
                id=clip_id,
                clip_id=clip_id,
                track_id=track_id,
                name="Clip",
                color=MsqColor(track_color="orange"),
                start=self.to_msq_ticks(clip_start),
                length=self.to_msq_ticks(clip_end - clip_start),
                notes=msq_notes,
                parameters=self.generate_parameters(track.edited_params, notes, clip_start),
            )
        ]

    def get_clip_start(self, params: Params, notes: list[Note]) -> int:
        return min(notes[0].start_pos, *self.get_param_curve_points(params))

    def get_clip_end(self, params: Params, notes: list[Note]) -> int:
        return max(notes[-1].end_pos, *self.get_param_curve_points(params))

    def get_param_curve_points(self, params: Params) -> list[int]:
        points: list[int] = []
        points.extend(self.get_curve_points(params.pitch, interrupt_value=-100))
        points.extend(self.get_curve_points(params.volume))
        points.extend(self.get_curve_points(params.breath))
        points.extend(self.get_curve_points(params.gender))
        points.extend(self.get_curve_points(params.strength))
        return points

    @staticmethod
    def get_curve_points(curve: ParamCurve, interrupt_value: int | None = None) -> list[int]:
        return [
            point.x
            for point in curve.points.root
            if 0 <= point.x < Point.end_point().x
            and (interrupt_value is None or point.y != interrupt_value)
        ]

    def generate_note(self, note: Note, clip_id: str, clip_start: int) -> MsqNote:
        phonemes = []
        return MsqNote(
            clip_id=clip_id,
            start=self.to_relative_msq_ticks(clip_start, note.start_pos),
            length=self.to_msq_ticks(note.length),
            pitch=float(note.key_number),
            lyric=note.lyric,
            phonemes=phonemes,
        )

    def generate_parameters(
        self,
        params: Params,
        notes: list[Note],
        clip_start: int,
    ) -> MsqParameters | None:
        parameters = MsqParameters()
        has_any_param = False
        if params.pitch.points and notes:
            pitch_points = self.generate_pitch_parameter(params.pitch, notes, clip_start)
            if pitch_points:
                parameters.pitch = MsqParameter(points=pitch_points)
                has_any_param = True
        if volume_points := self.generate_param_curve(params.volume, clip_start):
            parameters.dynamics = MsqParameter(points=volume_points)
            has_any_param = True
        if breath_points := self.generate_param_curve(params.breath, clip_start):
            parameters.breathiness = MsqParameter(points=breath_points)
            has_any_param = True
        if gender_points := self.generate_param_curve(params.gender, clip_start):
            parameters.character = MsqParameter(points=gender_points)
            has_any_param = True
        if strength_points := self.generate_param_curve(params.strength, clip_start):
            parameters.tension = MsqParameter(points=strength_points)
            has_any_param = True
        return parameters if has_any_param else None

    def generate_pitch_parameter(
        self,
        pitch: ParamCurve,
        notes: list[Note],
        clip_start: int,
    ) -> list[MsqPoint]:
        pitch_simulator = PitchSimulator(
            synchronizer=self.synchronizer,
            portamento=PortamentoPitch.no_portamento(),
            note_list=notes,
            time_signature_list=self.time_signatures,
        )
        relative_points: list[MsqPoint] = []
        for point_part in more_itertools.split_at(pitch.points.root, lambda point: point.y == -100):
            if point_part:
                relative_segment = RelativePitchCurve(self.first_bar_length).from_absolute(
                    point_part,
                    pitch_simulator,
                )
                relative_points.extend(
                    MsqPoint(
                        time=self.to_relative_msq_ticks(
                            clip_start, point.x + self.first_bar_length
                        ),
                        value=point.y / 100,
                    )
                    for point in relative_segment
                )
        return relative_points

    def generate_param_curve(self, curve: ParamCurve, clip_start: int) -> list[MsqPoint]:
        return [
            MsqPoint(
                time=self.to_relative_msq_ticks(clip_start, point.x),
                value=point.y / 1000,
            )
            for point in curve.points.root
            if 0 <= point.x < Point.end_point().x
        ]

    def generate_instrumental_track(
        self, track: InstrumentalTrack, index: int, out_id: str
    ) -> MsqAudioTrack:
        track_id = uuid_str()
        clip_id = uuid_str()
        clip_length = 0
        if (track_info := audio_track_info(track.audio_file_path)) is not None:
            clip_length = self.to_msq_ticks(
                int(
                    self.synchronizer.get_actual_ticks_from_secs_offset(
                        track.offset,
                        track_info.duration,
                    )
                    - track.offset
                )
            )
        return MsqAudioTrack(
            id=track_id,
            mixer=MsqMixer(
                gain=track.volume,
                pan=track.pan,
                record_arm=False,
                solo=track.solo,
                mute=track.mute,
                output=out_id,
            ),
            name=track.title,
            color="orange",
            index=index,
            track_type="Audio",
            instrument="AudioPlayer",
            clips=[
                MsqAudioClip(
                    id=clip_id,
                    clip_id=clip_id,
                    track_id=track_id,
                    name=track.title,
                    color="ThemeDefault",
                    start=self.to_msq_ticks(track.offset),
                    length=clip_length,
                    audio=MsqAudio(
                        path=track.audio_file_path,
                        start=0.0,
                        speed=1.0,
                        bpm=0.0,
                    ),
                )
            ],
        )
