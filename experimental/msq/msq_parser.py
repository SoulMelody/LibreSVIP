import dataclasses
import itertools
import operator

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.core.tick_counter import find_bar_index, skip_beat_list, skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Params,
    Points,
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

from .model import (
    MikotoStudioSequenceFormat,
    MsqAudioTrack,
    MsqBpmEvent,
    MsqNote,
    MsqParameter,
    MsqSingerClip,
    MsqSingerTrack,
    MsqTimeSignatureEvent,
)
from .options import InputOptions


@dataclasses.dataclass
class MsqParser:
    options: InputOptions
    ppq: float = TICKS_IN_BEAT

    def parse_project(self, msq_project: MikotoStudioSequenceFormat) -> Project:
        self.ppq = msq_project.setup.ppq or TICKS_IN_BEAT
        tracks: list[Track] = []
        tempos = self.parse_tempos(msq_project)
        time_signatures = self.parse_time_signatures(msq_project)

        for track in msq_project.tracks:
            if isinstance(track, MsqSingerTrack):
                tracks.append(self.parse_singing_track(track, tempos, time_signatures))
            elif isinstance(track, MsqAudioTrack) and self.options.import_instrumental_track:
                tracks.extend(self.parse_instrumental_tracks(track))

        return Project(
            song_tempo_list=skip_tempo_list(tempos, 0),
            time_signature_list=skip_beat_list(time_signatures, 0),
            track_list=tracks,
        )

    def to_ticks(self, value: int) -> int:
        return round(value * TICKS_IN_BEAT / self.ppq)

    def to_project_ticks(self, clip_start: int, value: int) -> int:
        return self.to_ticks(clip_start + value)

    def parse_tempos(self, msq_project: MikotoStudioSequenceFormat) -> list[SongTempo]:
        bpm_events = sorted(
            msq_project.setup.bpm_events
            or [MsqBpmEvent(position=0, bpm=msq_project.setup.bpm or DEFAULT_BPM)],
            key=operator.attrgetter("position"),
        )
        if bpm_events[0].position > 0:
            bpm_events.insert(
                0,
                MsqBpmEvent(position=0, bpm=msq_project.setup.bpm or DEFAULT_BPM),
            )
        return [
            SongTempo(
                position=self.to_ticks(event.position),
                bpm=event.bpm,
            )
            for event in bpm_events
        ]

    def parse_time_signatures(
        self,
        msq_project: MikotoStudioSequenceFormat,
    ) -> list[TimeSignature]:
        time_sig_events = sorted(
            msq_project.setup.time_signature_events
            or [
                MsqTimeSignatureEvent(
                    position=0,
                    time_sig=msq_project.setup.time_signature,
                )
            ],
            key=operator.attrgetter("position"),
        )
        time_signatures: list[TimeSignature] = []
        prev_position = 0
        prev_time_signature = msq_project.setup.time_signature
        bar_index = 0
        for i, event in enumerate(time_sig_events):
            if i == 0:
                bar_index = (
                    0
                    if event.position == 0
                    else round(
                        event.position
                        / (
                            self.ppq
                            * 4
                            * prev_time_signature.numerator
                            / prev_time_signature.denominator
                        )
                    )
                )
            else:
                bar_length = (
                    self.ppq * 4 * prev_time_signature.numerator / prev_time_signature.denominator
                )
                bar_index += round((event.position - prev_position) / bar_length)
            time_signatures.append(
                TimeSignature(
                    bar_index=bar_index,
                    numerator=event.time_sig.numerator,
                    denominator=event.time_sig.denominator,
                )
            )
            prev_position = event.position
            prev_time_signature = event.time_sig
        if not time_signatures or time_signatures[0].bar_index > 0:
            time_signatures.insert(
                0,
                TimeSignature(
                    bar_index=0,
                    numerator=msq_project.setup.time_signature.numerator,
                    denominator=msq_project.setup.time_signature.denominator,
                ),
            )
        return time_signatures

    def parse_singing_track(
        self,
        track: MsqSingerTrack,
        tempos: list[SongTempo],
        time_signatures: list[TimeSignature],
    ) -> SingingTrack:
        note_groups: list[tuple[MsqSingerClip, list[Note]]] = [
            (clip, self.parse_notes(clip))
            for clip in track.clips
            if isinstance(clip, MsqSingerClip)
        ]
        notes = sorted(
            itertools.chain.from_iterable(note_list for _, note_list in note_groups),
            key=operator.attrgetter("start_pos"),
        )
        self.validate_notes(notes, time_signatures)
        all_pitch_points: list[Point] = []
        if self.options.import_pitch:
            first_bar_length = (
                round(time_signatures[0].bar_length()) if time_signatures else TICKS_IN_BEAT * 4
            )
            for clip, clip_notes in note_groups:
                if clip.parameters and clip.parameters.pitch.points and clip_notes:
                    clip_pitch_points = self.get_pitch_points(
                        clip.parameters.pitch,
                        clip_notes,
                        tempos,
                        time_signatures,
                        first_bar_length,
                        clip.start,
                    )
                    all_pitch_points.extend(
                        point
                        for point in clip_pitch_points
                        if point.x not in {Point.start_point().x, Point.end_point().x}
                    )
        all_pitch_points.sort(key=operator.attrgetter("x"))
        params = Params()
        if all_pitch_points:
            params.pitch = ParamCurve(
                points=Points(root=[Point.start_point(), *all_pitch_points, Point.end_point()])
            )
        self.parse_params(note_groups, params)
        return SingingTrack(
            title=track.name,
            mute=track.mixer.mute,
            solo=track.mixer.solo,
            volume=track.mixer.gain,
            pan=track.mixer.pan,
            ai_singer_name=track.instrument.singer.name,
            note_list=notes,
            edited_params=params,
        )

    @staticmethod
    def validate_notes(notes: list[Note], time_signatures: list[TimeSignature]) -> None:
        for prev_note, note in itertools.pairwise(notes):
            if prev_note.end_pos > note.start_pos:
                msg = f"Notes overlapped near bar {find_bar_index(time_signatures, note.start_pos)}"
                raise NotesOverlappedError(msg)

    def parse_notes(self, clip: MsqSingerClip) -> list[Note]:
        return [self.parse_note(msq_note, clip.start) for msq_note in clip.notes or []]

    def parse_note(self, msq_note: MsqNote, clip_start: int) -> Note:
        pronunciation = " ".join(phoneme.phoneme for phoneme in msq_note.phonemes) or None
        return Note(
            start_pos=self.to_project_ticks(clip_start, msq_note.start),
            length=self.to_ticks(msq_note.length),
            key_number=int(msq_note.pitch),
            lyric=msq_note.lyric or "",
            pronunciation=pronunciation,
        )

    def parse_params(
        self,
        note_groups: list[tuple[MsqSingerClip, list[Note]]],
        params: Params,
    ) -> None:
        volume_points: list[Point] = []
        breath_points: list[Point] = []
        gender_points: list[Point] = []
        strength_points: list[Point] = []
        for clip, _clip_notes in note_groups:
            if clip.parameters is None:
                continue
            if self.options.import_volume:
                volume_points.extend(self.parse_param_curve(clip.parameters.dynamics, clip.start))
            if self.options.import_breath:
                breath_points.extend(
                    self.parse_param_curve(clip.parameters.breathiness, clip.start)
                )
            if self.options.import_gender:
                gender_points.extend(self.parse_param_curve(clip.parameters.character, clip.start))
            if self.options.import_strength:
                strength_points.extend(self.parse_param_curve(clip.parameters.tension, clip.start))
        if volume_points:
            params.volume = ParamCurve(
                points=Points(root=sorted(volume_points, key=operator.attrgetter("x")))
            )
        if breath_points:
            params.breath = ParamCurve(
                points=Points(root=sorted(breath_points, key=operator.attrgetter("x")))
            )
        if gender_points:
            params.gender = ParamCurve(
                points=Points(root=sorted(gender_points, key=operator.attrgetter("x")))
            )
        if strength_points:
            params.strength = ParamCurve(
                points=Points(root=sorted(strength_points, key=operator.attrgetter("x")))
            )

    def parse_param_curve(self, parameter: MsqParameter, clip_start: int) -> list[Point]:
        return [
            Point(
                x=self.to_project_ticks(clip_start, msq_point.time),
                y=round(msq_point.value * 1000),
            )
            for msq_point in sorted(parameter.points, key=operator.attrgetter("time"))
        ]

    def get_pitch_points(
        self,
        parameter: MsqParameter,
        notes: list[Note],
        tempos: list[SongTempo],
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        clip_start: int,
    ) -> list[Point]:
        synchronizer = TimeSynchronizer(tempos)
        pitch_simulator = PitchSimulator(
            synchronizer=synchronizer,
            portamento=PortamentoPitch.no_portamento(),
            note_list=notes,
            time_signature_list=time_signatures,
        )
        relative_points = [
            Point(
                x=self.to_project_ticks(clip_start, msq_point.time),
                y=round(msq_point.value * 100),
            )
            for msq_point in sorted(parameter.points, key=operator.attrgetter("time"))
        ]
        return (
            RelativePitchCurve(first_bar_length, is_staircase=False)
            .to_absolute(
                relative_points,
                pitch_simulator,
            )
            .points.root
        )

    def parse_instrumental_tracks(self, track: MsqAudioTrack) -> list[InstrumentalTrack]:
        return [
            InstrumentalTrack(
                title=clip.name or track.name,
                mute=track.mixer.mute,
                solo=track.mixer.solo,
                volume=track.mixer.gain,
                pan=track.mixer.pan,
                audio_file_path=clip.audio.path,
                offset=self.to_ticks(clip.start),
            )
            for clip in track.clips
            if clip.audio is not None
        ]
