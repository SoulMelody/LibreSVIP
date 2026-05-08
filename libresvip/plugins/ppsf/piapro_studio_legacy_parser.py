# mypy: disable-error-code="index,operator"
import dataclasses
from collections import defaultdict
from typing import Annotated

from construct import Container

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .legacy_model import PpsfChunk, PpsfLegacyProject
from .options import InputOptions


@dataclasses.dataclass
class PiaproStudioLegacyParser:
    options: InputOptions
    clip_offsets: list[int] = dataclasses.field(default_factory=list)
    clips2track_indexes: dict[int, int] = dataclasses.field(default_factory=dict)
    clips2note_indexes: dict[int, list[int]] = dataclasses.field(default_factory=dict)

    def parse_project(self, ppsf_project: Annotated[Container, PpsfLegacyProject]) -> Project:
        events_chunk: Annotated[Container, PpsfChunk] | None = None
        automation_id2event_indexes: dict[int, list[int]] = defaultdict(list)
        tempo_events: list[Container] = []
        meter_events: list[Container] = []
        for chunk in ppsf_project.chunks:
            match chunk.magic:
                case "Clips":
                    for i, clip in enumerate(chunk.data.vocaloid3_note_clips):
                        self.clip_offsets.append(clip.data.noteclip.offset)
                        self.clips2note_indexes[i] = clip.data.noteclip.iclip.event_indices
                    for clip in chunk.data.automation_clips:
                        automation_id2event_indexes[clip.index] = clip.data.event_indices
                case "Plugins":
                    for plugin in chunk.data.music_param_event_control_plugins:
                        if (
                            plugin.data.name == "Tempo"
                            and plugin.data.self_clip_idx in automation_id2event_indexes
                        ):
                            tempo_events.extend(
                                events_chunk[idx]
                                for idx in automation_id2event_indexes[plugin.data.self_clip_idx]
                            )
                        if (
                            plugin.data.name == "Meter"
                            and plugin.data.self_clip_idx in automation_id2event_indexes
                        ):
                            meter_events.extend(
                                events_chunk[idx]
                                for idx in automation_id2event_indexes[plugin.data.self_clip_idx]
                            )
                case "Events":
                    events_chunk = chunk.data
                case "Tracks":
                    clip_index: int
                    for i, track in enumerate(chunk.data.vocaloid3_event_tracks.data):
                        if track.magic == "Vocaloid3EventTrack":
                            for clip_index in track.data.clip_indices:
                                self.clips2track_indexes[clip_index] = i
        tempos, time_signatures = self.parse_tempos_and_time_signatures(
            tempo_events,
            meter_events,
        )
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=self.parse_tracks(events_chunk),
        )

    def parse_tempos_and_time_signatures(
        self,
        tempo_events: list[Container],
        meter_events: list[Container],
    ) -> tuple[list[SongTempo], list[TimeSignature]]:
        tempos = []
        time_signatures: list[TimeSignature] = []
        prev_tick = 0
        for event in tempo_events:
            tick = event.data.tick
            bpm = event.data.value / 10000
            tempos.append(
                SongTempo(
                    position=tick,
                    bpm=bpm,
                )
            )
        for event in meter_events:
            tick = event.data.tick
            denominator = event.data.value & 0xFF
            numerator = event.data.value >> 8
            if time_signatures:
                prev_bar_length = time_signatures[-1].bar_length()
                prev_bar_index = time_signatures[-1].bar_index
            else:
                prev_bar_length = TICKS_IN_BEAT * 4
                prev_bar_index = 0
            time_signatures.append(
                TimeSignature(
                    bar_index=prev_bar_index + (tick - prev_tick) // prev_bar_length,
                    numerator=numerator,
                    denominator=denominator,
                )
            )
            prev_tick = tick
        if not tempos:
            tempos.append(SongTempo())
        if not time_signatures:
            time_signatures.append(TimeSignature())
        return tempos, time_signatures

    def parse_tracks(self, events_chunk: Container | None = None) -> list[SingingTrack]:
        tracks: list[SingingTrack] = []
        if events_chunk is not None:
            track_index2notes = defaultdict(list)
            for clip_index, note_group in self.clips2note_indexes.items():
                track_index = self.clips2track_indexes[clip_index]
                for note_index in note_group:
                    note = events_chunk[note_index]
                    track_index2notes[track_index].append(
                        Note(
                            start_pos=self.clip_offsets[clip_index] + note.data.tick,
                            length=note.data.duration,
                            key_number=note.data.note,
                            lyric=note.data.lyric,
                            pronunciation=note.data.phoneme,
                        )
                    )
            tracks.extend(SingingTrack(note_list=notes) for notes in track_index2notes.values())
        return tracks
