from __future__ import annotations

import dataclasses
import pathlib
from typing import TYPE_CHECKING, TypeVar

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Project,
    SingingTrack,
    SongTempo,
)
from libresvip.model.base import (
    Note as LibreNote,
)
from libresvip.model.base import (
    TimeSignature as LibreTimeSignature,
)
from libresvip.model.base import (
    Track as LibreTrack,
)
from libresvip.utils.music_math import clamp, db_to_float

from .model_v1 import (
    AudioClip,
    BusControl,
    Model,
    Note,
    SingingClip,
    Track,
)
from .options import InputOptions, VibratoImportMode
from .param_utils import ResolvedParam, build_pitch_curve
from .vibrato_utils import VibratoSequence, import_vibrato

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


def _last_by_position(items: list[T], position: Callable[[T], int]) -> list[T]:
    result: dict[int, T] = {}
    for item in items:
        result[position(item)] = item
    return [result[key] for key in sorted(result)]


@dataclasses.dataclass
class DspxParser:
    options: InputOptions
    path: pathlib.Path
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    master_control: BusControl = dataclasses.field(init=False)

    def parse_project(self, model: Model) -> Project:
        tempos = self.parse_tempos(model)
        time_signatures = self.parse_time_signatures(model)
        self.first_bar_length = round(time_signatures[0].bar_length())
        self.synchronizer = TimeSynchronizer(tempos)
        self.master_control = model.content.master.control
        return Project(
            version=model.version,
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=self.parse_tracks(model.content.tracks),
        )

    @staticmethod
    def parse_tempos(model: Model) -> list[SongTempo]:
        source = _last_by_position(model.content.timeline.tempos, lambda tempo: tempo.pos)
        tempos = [SongTempo(position=tempo.pos, bpm=tempo.value) for tempo in source]
        if not tempos or tempos[0].position > 0:
            tempos.insert(0, SongTempo(position=0, bpm=DEFAULT_BPM))
        return tempos

    @staticmethod
    def parse_time_signatures(model: Model) -> list[LibreTimeSignature]:
        source = _last_by_position(
            model.content.timeline.time_signatures,
            lambda time_signature: time_signature.index,
        )
        time_signatures = [
            LibreTimeSignature(
                bar_index=time_signature.index,
                numerator=time_signature.numerator,
                denominator=time_signature.denominator,
            )
            for time_signature in source
        ]
        if not time_signatures or time_signatures[0].bar_index > 0:
            time_signatures.insert(
                0,
                LibreTimeSignature(bar_index=0, numerator=4, denominator=4),
            )
        return time_signatures

    def parse_tracks(self, tracks: list[Track]) -> list[LibreTrack]:
        result: list[LibreTrack] = []
        for track in tracks:
            for clip in track.clips:
                if isinstance(clip, AudioClip):
                    result.append(self.parse_audio_clip(track, clip))
                else:
                    result.append(self.parse_singing_clip(track, clip))
        return result

    def parse_common_track_fields(
        self,
        track: Track,
        clip: AudioClip | SingingClip,
    ) -> dict[str, object]:
        total_gain = clamp(
            self.master_control.gain + track.control.gain + clip.control.gain,
            -400,
            400,
        )
        return {
            "title": clip.name or track.name,
            "volume": db_to_float(total_gain),
            "pan": clamp(
                self.master_control.pan + track.control.pan + clip.control.pan,
                -1,
                1,
            ),
            "mute": self.master_control.mute or track.control.mute or clip.control.mute,
            "solo": track.control.solo,
        }

    def parse_audio_clip(self, track: Track, clip: AudioClip) -> InstrumentalTrack:
        audio_path = pathlib.Path(clip.path)
        if not audio_path.is_absolute():
            audio_path = (self.path.parent / audio_path).resolve()
        return InstrumentalTrack(
            **self.parse_common_track_fields(track, clip),
            audio_file_path=str(audio_path),
            offset=clip.time.pos - clip.time.clip_start,
        )

    def parse_singing_clip(self, track: Track, clip: SingingClip) -> SingingTrack:
        clip_start = clip.time.pos - clip.time.clip_start
        source_notes = [note for note in clip.notes if note.length > 0 and bool(note.lyric.strip())]
        note_list = [self.parse_note(note, clip_start) for note in source_notes]
        singing_track = SingingTrack(
            **self.parse_common_track_fields(track, clip),
            note_list=note_list,
        )
        if self.options.import_pitch and (pitch_parameter := clip.params.get("pitch")):
            pitch = ResolvedParam(pitch_parameter, self.options.pitch_import_mode)
            vibrato_value = None
            if self.options.vibrato_import_mode == VibratoImportMode.BAKE_TO_PITCH:
                vibrato_sequence = VibratoSequence(
                    source_notes,
                    clip_start=clip_start,
                    synchronizer=self.synchronizer,
                )

                def vibrato_value(relative_tick: int) -> float:
                    return vibrato_sequence.evaluate(
                        relative_tick,
                        clip_start,
                    )

            singing_track.edited_params.pitch = build_pitch_curve(
                pitch,
                coordinate_offset=clip_start + self.first_bar_length,
                vibrato_value=vibrato_value,
            )
        return singing_track

    def parse_note(self, note: Note, clip_start: int) -> LibreNote:
        vibrato = (
            import_vibrato(note.vibrato)
            if self.options.vibrato_import_mode == VibratoImportMode.PRESERVE
            else None
        )
        return LibreNote(
            start_pos=note.pos + clip_start,
            length=note.length,
            key_number=note.key_num,
            lyric=note.lyric,
            vibrato=vibrato,
        )
