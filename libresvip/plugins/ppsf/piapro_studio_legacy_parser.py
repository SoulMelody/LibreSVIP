import dataclasses
import struct
from collections import defaultdict
from typing import Optional

from construct import (
    Byte,
    Container,
    Int16ul,
    PascalString,
    PrefixedArray,
    Struct,
)
from more_itertools import split_into

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
    clip_note_counts: list[int] = dataclasses.field(default_factory=list)
    clips2track_indexes: dict[int, int] = dataclasses.field(default_factory=dict)

    def parse_project(self, ppsf_project: PpsfLegacyProject) -> Project:
        events_chunk: Optional[PpsfChunk] = None
        for chunk in ppsf_project.body.chunks:
            if chunk.magic == "Clips":
                for clip_group in chunk.data.clips:
                    for clip in clip_group:
                        if clip.magic == "Vocaloid3NoteClip":
                            (clip_offset,) = struct.unpack_from(
                                "<i", clip.data, len(clip.data) - 32
                            )
                            self.clip_offsets.append(clip_offset)
            elif chunk.magic == "EditorDatas":
                for track_data in chunk.data.editor_datas:
                    for clip_data in track_data.data.clip_datas:
                        self.clip_note_counts.append(len(clip_data.data.note_datas))
            elif chunk.magic == "Events":
                events_chunk = chunk
            elif chunk.magic == "Tracks":
                clip_indexes_struct = Struct(
                    PascalString(Byte, "utf-8"),
                    "indexes" / PrefixedArray(Byte, Int16ul),
                )
                for track_group in chunk.data.tracks:
                    if track_group.magic == "Vocaloid3EventTracks":
                        clip_index = 0
                        for i, track in enumerate(track_group.data):
                            clip_indexes = clip_indexes_struct.parse(track.data[30:])
                            for clip_index in clip_indexes.indexes:
                                self.clips2track_indexes[clip_index] = i
        tempos, time_signatures = self.parse_tempos_and_time_signatures(events_chunk)
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=self.parse_tracks(events_chunk),
        )

    def parse_tempos_and_time_signatures(
        self, events_chunk: Optional[Container] = None
    ) -> tuple[list[SongTempo], list[TimeSignature]]:
        tempos = []
        time_signatures: list[TimeSignature] = []
        if events_chunk is not None:
            prev_tick = -TICKS_IN_BEAT * 4
            for event_group in events_chunk.data.events:
                events_by_level: list[list[tuple[int, bytes]]] = []
                for event in event_group:
                    if event.magic == "MidiEvent":
                        (tick,) = struct.unpack_from(
                            "<i",
                            event.data,
                        )
                        if event.data[-1] == 0:
                            if tick == 0:
                                events_by_level.append([])
                            if len(events_by_level):
                                events_by_level[-1].append((tick, event.data))

                if len(events_by_level) > 1:
                    for tick, event_data in events_by_level[-2]:
                        bpm = struct.unpack_from("<i", event_data, 4)[0] / 10000
                        tempos.append(
                            SongTempo(
                                position=tick,
                                bpm=bpm,
                            )
                        )
                    for tick, event_data in events_by_level[-1]:
                        (denominator, numerator) = struct.unpack_from("<2b", event_data, 4)
                        if len(time_signatures):
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

    def parse_tracks(self, events_chunk: Optional[Container] = None) -> list[SingingTrack]:
        tracks: list[SingingTrack] = []
        if events_chunk is not None:
            lyric_info_struct = Struct(
                "lyric" / PascalString(Byte, "utf-8"),
                Byte,
                "phoneme" / PascalString(Byte, "utf-8"),
                Byte,
            )
            track_index2notes = defaultdict(list)
            note_events = [
                event
                for event_group in events_chunk.data.events
                for event in event_group
                if event.magic == "Vocaloid3NoteEvent"
            ]
            for i, note_group in enumerate(split_into(note_events, self.clip_note_counts)):
                for note in note_group:
                    note_offset, pit, length = struct.unpack_from(
                        "<ibi",
                        note.data,
                    )
                    lyric_info = lyric_info_struct.parse(note.data[16:])
                    track_index2notes[self.clips2track_indexes[i]].append(
                        Note(
                            start_pos=self.clip_offsets[i] + note_offset,
                            length=length,
                            key_number=pit,
                            lyric=lyric_info.lyric,
                            pronunciation=lyric_info.phoneme,
                        )
                    )
            tracks.extend(SingingTrack(note_list=notes) for notes in track_index2notes.values())
        return tracks
