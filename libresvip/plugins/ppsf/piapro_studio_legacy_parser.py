# mypy: disable-error-code="index,operator"
import dataclasses
from collections import defaultdict
from typing import Annotated

from construct import Container

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.vocaloid.controller_models import ControllerCurve, ControllerEvent
from libresvip.model.vocaloid.pitch_handler import PitchBendData, VocaloidPitchHandler
from libresvip.utils.binary.midi import DEFAULT_PITCH_BEND_SENSITIVITY, PITCH_MAX_VALUE

from .legacy_model import (
    V3_PARAM_PBS_INDEX,
    V3_PARAM_PIT_INDEX,
    PpsfLegacyProject,
)
from .options import InputOptions

PIT_CENTER = 64
PIT_RANGE = 64


@dataclasses.dataclass
class PiaproStudioLegacyParser:
    options: InputOptions
    clip_offsets: list[int] = dataclasses.field(default_factory=list)
    clips2track_indexes: dict[int, int] = dataclasses.field(default_factory=dict)
    clips2note_indexes: dict[int, list[int]] = dataclasses.field(default_factory=dict)

    def parse_project(self, ppsf_project: Annotated[Container, PpsfLegacyProject]) -> Project:
        events_chunk: Container | None = None
        automation_id2event_indexes: dict[int, list[int]] = defaultdict(list)
        tempo_events: list[Container] = []
        meter_events: list[Container] = []
        track_plugin_indices: dict[int, list[int]] = {}
        plugin_pit_clip: dict[int, int] = {}
        pit_indices_by_clip: dict[int, list[int]] = {}
        pbs_indices_by_clip: dict[int, list[int]] = {}

        for chunk in ppsf_project.chunks:
            match chunk.magic:
                case "Clips":
                    for i, clip in enumerate(chunk.data.vocaloid3_note_clips):
                        self.clip_offsets.append(clip.data.noteclip.offset)
                        self.clips2note_indexes[i] = clip.data.noteclip.iclip.event_indices
                    for clip in chunk.data.automation_clips:
                        automation_id2event_indexes[clip.index] = clip.data.event_indices
                        if (
                            clip.data.field_4 == 11
                            and len(clip.data.sub_event_indices) >= V3_PARAM_PBS_INDEX
                        ):
                            pit_indices_by_clip[clip.index] = list(
                                clip.data.sub_event_indices[V3_PARAM_PIT_INDEX - 1]
                            )
                            pbs_indices_by_clip[clip.index] = list(
                                clip.data.sub_event_indices[V3_PARAM_PBS_INDEX - 1]
                            )
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
                    for plugin in chunk.data.vocaloid3_event_control_plugins:
                        if plugin.data.name == "Vocaloid3 Parameter":
                            plugin_pit_clip[plugin.index] = plugin.data.self_clip_idx
                case "Events":
                    events_chunk = chunk.data
                case "Tracks":
                    clip_index: int
                    for i, track in enumerate(chunk.data.vocaloid3_event_tracks.data):
                        if track.magic == "Vocaloid3EventTrack":
                            for clip_index in track.data.clip_indices:
                                self.clips2track_indexes[clip_index] = i
                            track_plugin_indices[i] = list(track.data.base.v3_event_plugin_indices)

        pit_clip_by_track: dict[int, int] = {}
        for track_idx, plugin_list in track_plugin_indices.items():
            for plugin_idx in plugin_list:
                if plugin_idx in plugin_pit_clip:
                    pit_clip_by_track[track_idx] = plugin_pit_clip[plugin_idx]
                    break

        tempos, time_signatures = self.parse_tempos_and_time_signatures(
            tempo_events,
            meter_events,
        )
        synchronizer = TimeSynchronizer(tempos)
        first_bar_length = (
            round(time_signatures[0].bar_length()) if time_signatures else TICKS_IN_BEAT * 4
        )
        return Project(
            song_tempo_list=tempos,
            time_signature_list=time_signatures,
            track_list=self.parse_tracks(
                events_chunk,
                time_signatures,
                first_bar_length,
                synchronizer,
                pit_clip_by_track,
                pit_indices_by_clip,
                pbs_indices_by_clip,
            ),
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

    def parse_tracks(
        self,
        events_chunk: Container | None,
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        synchronizer: TimeSynchronizer,
        pit_clip_by_track: dict[int, int],
        pit_indices_by_clip: dict[int, list[int]],
        pbs_indices_by_clip: dict[int, list[int]],
    ) -> list[SingingTrack]:
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
            for track_index, notes in track_index2notes.items():
                singing_track = SingingTrack(note_list=notes)
                if self.options.import_pitch and notes and track_index in pit_clip_by_track:
                    clip_idx = pit_clip_by_track[track_index]
                    pit_event_indices = pit_indices_by_clip.get(clip_idx, [])
                    pbs_event_indices = pbs_indices_by_clip.get(clip_idx, [])
                    if pit_event_indices:
                        pitch = self._parse_pitch(
                            events_chunk,
                            pit_event_indices,
                            pbs_event_indices,
                            notes,
                            time_signatures,
                            first_bar_length,
                            synchronizer,
                        )
                        if pitch is not None:
                            singing_track.edited_params.pitch = pitch
                tracks.append(singing_track)
        return tracks

    @staticmethod
    def _parse_pitch(
        events_chunk: Container,
        pit_event_indices: list[int],
        pbs_event_indices: list[int],
        notes: list[Note],
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        synchronizer: TimeSynchronizer,
    ) -> ParamCurve | None:
        pit_events = []
        for idx in pit_event_indices:
            event = events_chunk[idx]
            raw_value = event.data.value
            if raw_value >= 0x80000000:
                raw_value -= 0x100000000
            pit_events.append(ControllerEvent(pos=event.data.tick, value=raw_value))

        if not pit_events:
            return None

        pbs_events = []
        for idx in pbs_event_indices:
            event = events_chunk[idx]
            pbs_events.append(ControllerEvent(pos=event.data.tick, value=event.data.value))

        handler = VocaloidPitchHandler(
            synchronizer=synchronizer,
            note_list=notes,
            time_signature_list=time_signatures,
            first_bar_length=first_bar_length,
        )
        pit_curve = ControllerCurve(
            name="pitch_bend",
            events=pit_events,
            default_value=0,
            min_value=-PITCH_MAX_VALUE - 1,
            max_value=PITCH_MAX_VALUE,
        )
        pbs_curve = ControllerCurve(
            name="pitch_bend_sens",
            events=pbs_events,
            default_value=DEFAULT_PITCH_BEND_SENSITIVITY,
            min_value=1,
            max_value=24,
        )
        pitch_data = PitchBendData(pit=pit_curve, pbs=pbs_curve)
        return handler.to_absolute_pitch([pitch_data], [0])
