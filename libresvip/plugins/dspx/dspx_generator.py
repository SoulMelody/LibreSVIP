from __future__ import annotations

import dataclasses
import math
from pathlib import Path

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note as LibreNote,
    ParamCurve as LibreParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature as LibreTimeSignature,
    Track as LibreTrack,
)
from libresvip.model.point import Point
from libresvip.utils.audio import audio_track_info
from libresvip.utils.music_math import clamp, ratio_to_db

from .model_v1 import (
    INT32_MAX,
    AudioClip,
    BusControl,
    ClipTime,
    Content,
    Global,
    Master,
    Model,
    Note,
    Phonemes,
    Pronunciation,
    SingingClip,
    Tempo,
    TimeSignature,
    Timeline,
    Track,
    TrackControl,
)
from .options import OutputOptions
from .param_utils import export_pitch_param
from .vibrato_utils import export_vibrato

VALID_DENOMINATORS = (1, 2, 4, 8, 16, 32, 64, 128)


def _clamp_int32(value: int | float, *, lower: int = 0) -> int:
    return round(clamp(round(value), lower, INT32_MAX))


def _linear_volume_to_db(volume: float) -> float:
    if not math.isfinite(volume):
        return 0.0
    if volume <= 0:
        return -70.0
    result = ratio_to_db(volume)
    return result if math.isfinite(result) else -70.0


@dataclasses.dataclass
class DspxGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> Model:
        tempos = self.generate_tempos(project.song_tempo_list)
        time_signatures = self.generate_time_signatures(project.time_signature_list)
        self.first_bar_length = round(
            LibreTimeSignature(
                bar_index=time_signatures[0].index,
                numerator=time_signatures[0].numerator,
                denominator=time_signatures[0].denominator,
            ).bar_length()
        )
        self.synchronizer = TimeSynchronizer(
            [SongTempo(position=tempo.pos, bpm=tempo.value) for tempo in tempos]
        )
        return Model(
            version="1.0.0",
            content=Content(
                global_=Global(
                    author="",
                    centShift=0,
                    editorId="libresvip",
                    editorName="LibreSVIP",
                    name="",
                ),
                master=Master(control=BusControl(gain=0, mute=False, pan=0)),
                timeline=Timeline(
                    labels=[],
                    tempos=tempos,
                    timeSignatures=time_signatures,
                ),
                tracks=self.generate_tracks(project.track_list),
                workspace={},
            ),
        )

    @staticmethod
    def generate_tempos(tempos: list[SongTempo]) -> list[Tempo]:
        normalized: dict[int, Tempo] = {}
        for tempo in tempos:
            if not math.isfinite(tempo.bpm):
                continue
            position = _clamp_int32(tempo.position)
            normalized[position] = Tempo(
                pos=position,
                value=clamp(tempo.bpm, 10, 1000),
            )
        normalized.setdefault(0, Tempo(pos=0, value=DEFAULT_BPM))
        return [normalized[position] for position in sorted(normalized)]

    @staticmethod
    def generate_time_signatures(
        time_signatures: list[LibreTimeSignature],
    ) -> list[TimeSignature]:
        normalized: dict[int, TimeSignature] = {}
        for time_signature in time_signatures:
            position = _clamp_int32(time_signature.bar_index)
            normalized[position] = TimeSignature(
                index=position,
                numerator=_clamp_int32(time_signature.numerator, lower=1),
                denominator=(
                    time_signature.denominator
                    if time_signature.denominator in VALID_DENOMINATORS
                    else 4
                ),
            )
        normalized.setdefault(0, TimeSignature(index=0, numerator=4, denominator=4))
        return [normalized[position] for position in sorted(normalized)]

    def generate_tracks(self, tracks: list[LibreTrack]) -> list[Track]:
        result: list[Track] = []
        for track in tracks:
            if isinstance(track, InstrumentalTrack):
                clip = self.generate_audio_clip(track)
            else:
                clip = self.generate_singing_clip(track)
            result.append(
                Track(
                    name=track.title,
                    control=self.generate_track_control(track),
                    clips=[clip],
                    workspace={},
                )
            )
        return result

    @staticmethod
    def generate_track_control(track: LibreTrack) -> TrackControl:
        return TrackControl(
            gain=_linear_volume_to_db(track.volume),
            pan=clamp(track.pan if math.isfinite(track.pan) else 0, -1, 1),
            mute=bool(track.mute),
            solo=bool(track.solo),
        )

    @staticmethod
    def neutral_clip_control() -> BusControl:
        return BusControl(gain=0, mute=False, pan=0)

    def generate_audio_clip(self, track: InstrumentalTrack) -> AudioClip:
        offset = round(track.offset)
        pos = _clamp_int32(max(offset, 0))
        clip_start = _clamp_int32(max(-offset, 0))
        duration = 0
        if (info := audio_track_info(track.audio_file_path)) is not None:
            actual_start = pos - clip_start
            duration = _clamp_int32(
                self.synchronizer.get_actual_ticks_from_secs_offset(
                    actual_start,
                    info.duration,
                )
                - actual_start
            )
        return AudioClip(
            type="audio",
            name=track.title,
            path=str(Path(track.audio_file_path)),
            time=ClipTime(
                pos=pos,
                length=duration,
                clipStart=clip_start,
                clipLen=max(duration - clip_start, 0),
            ),
            control=self.neutral_clip_control(),
            workspace={},
        )

    def generate_singing_clip(self, track: SingingTrack) -> SingingClip:
        source_notes = [
            note
            for note in track.note_list
            if note.length > 0 and bool(note.lyric.strip())
        ]
        origin = self.find_clip_origin(source_notes, track.edited_params.pitch)
        clip_start = _clamp_int32(-origin)
        notes = [
            generated
            for note in source_notes
            if (generated := self.generate_note(note, origin)) is not None
        ]
        params = {}
        if self.options.export_pitch and (
            pitch := export_pitch_param(
                track.edited_params.pitch,
                coordinate_offset=self.first_bar_length + origin,
            )
        ):
            params["pitch"] = pitch
        max_end = max([0, *(origin + note.pos + note.length for note in notes)])
        pitch_end = self.pitch_end(track.edited_params.pitch)
        if pitch_end is not None:
            max_end = max(max_end, pitch_end)
        length = _clamp_int32(max_end - origin)
        return SingingClip(
            type="singing",
            name=track.title,
            time=ClipTime(
                pos=0,
                length=length,
                clipStart=clip_start,
                clipLen=_clamp_int32(max_end),
            ),
            control=self.neutral_clip_control(),
            notes=notes,
            params=params,
            sources=None,
            workspace={},
        )

    def find_clip_origin(
        self,
        notes: list[LibreNote],
        pitch: LibreParamCurve,
    ) -> int:
        positions = [0, *(note.start_pos for note in notes)]
        positions.extend(
            point.x - self.first_bar_length
            for point in pitch.points.root
            if point.x not in (Point.start_point().x, Point.end_point().x)
        )
        return max(-INT32_MAX, min(positions))

    def pitch_end(self, pitch: LibreParamCurve) -> int | None:
        positions = [
            point.x - self.first_bar_length
            for point in pitch.points.root
            if point.x not in (Point.start_point().x, Point.end_point().x)
            and point.y != -100
        ]
        return max(positions) if positions else None

    def generate_note(self, note: LibreNote, origin: int) -> Note | None:
        relative_pos = note.start_pos - origin
        if relative_pos < 0 or relative_pos > INT32_MAX:
            return None
        return Note(
            pos=relative_pos,
            length=_clamp_int32(note.length, lower=1),
            keyNum=round(clamp(note.key_number, 0, 127)),
            centShift=0,
            language="",
            lyric=note.lyric,
            pronunciation=Pronunciation(original="", edited=""),
            phonemes=Phonemes(original=[], edited=[]),
            vibrato=export_vibrato(
                note.vibrato,
                preserve=self.options.preserve_vibrato,
            ),
            workspace={},
        )
