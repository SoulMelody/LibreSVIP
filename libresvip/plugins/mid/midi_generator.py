import dataclasses
import operator
from typing import Any, TypeAlias

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.binary.midi import bpm2tempo
from libresvip.utils.text import SYMBOL_PATTERN

from .constants import ControlChange
from .midi_pitch import generate_for_midi
from .options import OutputOptions

MidiMessage: TypeAlias = dict[str, Any]


@dataclasses.dataclass
class MidiGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)

    @property
    def tick_rate(self) -> float:
        return TICKS_IN_BEAT / self.options.ticks_per_beat

    def generate_project(self, project: Project) -> dict[str, Any]:
        self.first_bar_length = round(
            project.time_signature_list[0].bar_length(self.options.ticks_per_beat)
        )
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        mido_obj: dict[str, Any] = {
            "type": 1,
            "ticks_per_beat": self.options.ticks_per_beat,
        }
        tracks: list[list[MidiMessage]] = []
        master_track: list[MidiMessage] = []
        self.generate_tempos(master_track, project.song_tempo_list)
        self.generate_time_signatures(master_track, project.time_signature_list)
        master_track.append(
            {
                "time": master_track[-1]["time"] if master_track else 0,
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x2F,
                    "data": {"type": "end_of_track"},
                },
            }
        )
        master_track.sort(key=operator.itemgetter("time"))
        tracks.append(master_track)
        tracks.extend(self.generate_tracks(project.track_list, project.time_signature_list))
        self._convert_cumulative_to_delta(tracks)
        mido_obj["tracks"] = tracks
        return mido_obj

    @staticmethod
    def _convert_cumulative_to_delta(tracks: list[list[MidiMessage]]) -> None:
        for track in tracks:
            tick = 0
            for event in track:
                tick, event["time"] = event["time"], event["time"] - tick

    def generate_tempos(
        self, master_track: list[MidiMessage], song_tempo_list: list[SongTempo]
    ) -> None:
        master_track.extend(
            {
                "time": round(tempo.position / self.tick_rate),
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x51,
                    "data": {
                        "type": "set_tempo",
                        "tempo": bpm2tempo(tempo.bpm),
                    },
                },
            }
            for tempo in song_tempo_list
            if tempo.position >= 0
        )

    def generate_time_signatures(
        self,
        master_track: list[MidiMessage],
        time_signature_list: list[TimeSignature],
    ) -> None:
        prev_ticks = 0
        prev_time_signature = None
        for time_signature in time_signature_list:
            if time_signature.bar_index >= 0:
                if prev_time_signature is not None:
                    prev_ticks += round(
                        (time_signature.bar_index - prev_time_signature.bar_index)
                        * prev_time_signature.bar_length(self.options.ticks_per_beat)
                    )
                master_track.append(
                    {
                        "time": prev_ticks,
                        "__next": 0xFF,
                        "status": 0xFF,
                        "detail": {
                            "type": "meta",
                            "event_type": 0x58,
                            "data": {
                                "type": "time_signature",
                                "numerator": time_signature.numerator,
                                "denominator": time_signature.denominator,
                                "clocks_per_click": 24,
                                "notated_32nd_notes_per_quarter": 8,
                            },
                        },
                    }
                )
                prev_time_signature = time_signature

    def generate_tracks(
        self, tracks: list[Track], time_signature_list: list[TimeSignature]
    ) -> list[list[MidiMessage]]:
        return [
            mido_track
            for track in tracks
            if isinstance(track, SingingTrack)
            and (mido_track := self.generate_track(track, time_signature_list)) is not None
        ]

    def generate_track(
        self, track: SingingTrack, time_signature_list: list[TimeSignature]
    ) -> list[MidiMessage] | None:
        lyrics = [
            note.pronunciation if note.pronunciation is not None else note.lyric
            for note in track.note_list
        ]
        if self.options.remove_symbols:
            lyrics = [SYMBOL_PATTERN.sub("", lyric) for lyric in lyrics]
        pinyins = get_pinyin_series(lyrics)
        mido_track: list[MidiMessage] = [
            {
                "time": 0,
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x03,
                    "data": {
                        "type": "track_name",
                        "name": track.title.encode(self.options.lyric_encoding, "replace"),
                    },
                },
            }
        ]
        for i, note in enumerate(track.note_list):
            if self.options.export_lyrics:
                mido_track.append(
                    {
                        "time": round(note.start_pos / self.tick_rate),
                        "__next": 0xFF,
                        "status": 0xFF,
                        "detail": {
                            "type": "meta",
                            "event_type": 0x05,
                            "data": {
                                "type": "lyrics",
                                "text": (
                                    pinyins[i] if self.options.compatible_lyric else lyrics[i]
                                ).encode(self.options.lyric_encoding, "replace"),
                            },
                        },
                    }
                )
            mido_track.extend(
                (
                    {
                        "time": round(note.start_pos / self.tick_rate),
                        "__next": 0x90,
                        "status": 0x90,
                        "detail": {
                            "type": "channel",
                            "data": {
                                "type": "note_on",
                                "note": note.key_number,
                                "velocity": 127,
                            },
                        },
                    },
                    {
                        "time": round(note.end_pos / self.tick_rate),
                        "__next": 0x80,
                        "status": 0x80,
                        "detail": {
                            "type": "channel",
                            "data": {
                                "type": "note_off",
                                "note": note.key_number,
                                "velocity": 0,
                            },
                        },
                    },
                )
            )
        if pitch_data := generate_for_midi(
            self.first_bar_length,
            track.edited_params.pitch,
            track.note_list,
            time_signature_list,
            self.synchronizer,
        ):
            for pbs_event in pitch_data.pbs:
                msg_time = round(pbs_event.tick / self.tick_rate)
                mido_track.extend(
                    [
                        {
                            "time": msg_time,
                            "__next": 0xB0,
                            "status": 0xB0,
                            "detail": {
                                "type": "channel",
                                "data": {
                                    "type": "control_change",
                                    "control": ControlChange.RPN_MSB.value,
                                    "value": 0,
                                },
                            },
                        },
                        {
                            "time": msg_time,
                            "__next": 0xB0,
                            "status": 0xB0,
                            "detail": {
                                "type": "channel",
                                "data": {
                                    "type": "control_change",
                                    "control": ControlChange.RPN_LSB.value,
                                    "value": 0,
                                },
                            },
                        },
                        {
                            "time": msg_time,
                            "__next": 0xB0,
                            "status": 0xB0,
                            "detail": {
                                "type": "channel",
                                "data": {
                                    "type": "control_change",
                                    "control": ControlChange.DATA_ENTRY.value,
                                    "value": pbs_event.value,
                                },
                            },
                        },
                    ]
                )
            mido_track.extend(
                {
                    "time": round(pitch_event.tick / self.tick_rate),
                    "__next": 0xE0,
                    "status": 0xE0,
                    "detail": {
                        "type": "channel",
                        "data": {
                            "type": "pitchwheel",
                            "pitch": pitch_event.value,
                        },
                    },
                }
                for pitch_event in pitch_data.pit
            )
        mido_track.sort(key=operator.itemgetter("time"))
        if mido_track:
            mido_track.append(
                {
                    "time": mido_track[-1]["time"],
                    "__next": 0xFF,
                    "status": 0xFF,
                    "detail": {
                        "type": "meta",
                        "event_type": 0x2F,
                        "data": {"type": "end_of_track"},
                    },
                }
            )
            return mido_track
