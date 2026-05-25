import dataclasses

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    TimeSignature,
)
from libresvip.model.vocaloid.pitch_handler import VocaloidPitchHandler
from libresvip.utils.binary.midi import PITCH_MAX_VALUE

from .constants import (
    DEFAULT_TOTAL_MEASURES,
    DEFAULT_VELOCITY,
    EFFECT_TRACK_INDEX,
    EFFECT_TYPE_PIT,
    EFFECT_TYPES_ORDER,
    MASTER_TRACK_INDEX,
    MAX_EFFECT_ENTRIES,
    TICKS_IN_WHOLE_NOTE,
    VSP_PIT_CENTER,
    VSP_PIT_RANGE,
)
from .options import OutputOptions

AnyDict = dict[str, object]

EFFECT_DEFAULTS: dict[int, tuple[int, int]] = {
    0: (1, VSP_PIT_CENTER),
    6: (1, 0),
    17: (1, 0),
    1: (1, 168),
    12: (1, 0),
    13: (1, 0),
    14: (1, 0),
    7: (1, 0),
    11: (1, 30),
    8: (1, 110),
    15: (0, 0),
    16: (0, 0),
}


def _vocaloid_pit_to_vsp(pit: int) -> int:
    value = round(pit / PITCH_MAX_VALUE * VSP_PIT_RANGE + VSP_PIT_CENTER)
    return max(0, min(127, value))


def _linear_to_packed(pos: int, ticks_per_beat: int, beats_per_bar: int) -> dict[str, int]:
    ticks_per_bar = ticks_per_beat * beats_per_bar
    bar = pos // ticks_per_bar
    remainder = pos % ticks_per_bar
    beat = remainder // ticks_per_beat
    tick = remainder % ticks_per_beat
    return {
        "low": tick,
        "mid": beat,
        "high": bar,
    }


def _linear_to_packed_raw(pos: int, ticks_per_beat: int, beats_per_bar: int) -> int:
    ticks_per_bar = ticks_per_beat * beats_per_bar
    bar = pos // ticks_per_bar
    remainder = pos % ticks_per_bar
    beat = remainder // ticks_per_beat
    tick = remainder % ticks_per_beat
    return tick | (beat << 12) | (bar << 16)


def _track_dict(title: str, singer_name: str, volume: int = 100, pan: int = 50) -> AnyDict:
    return {
        "track_name": title,
        "singer_name": singer_name,
        "volume": volume,
        "param_block": {
            "wstring": "",
            "params_1_7": [168, 0, 0, 0, 240, 0, 0],
            "params_11_14": [30, 0, 0, 0],
            "sub_46E220_1": {"f1": 0.0, "f2": 0.0, "f0": 0.0},
            "sub_46E220_2": {"f1": 0.0, "f2": 0.0, "f0": 0.0},
            "sub_46E220_3": {"f1": 0.0, "f2": 0.0, "f0": 0.0},
            "sub_46E270": {"v0": 0, "v4": 0, "v8": 0, "f12": 0.0, "v16": 0},
            "param_17": 0,
        },
        "pan": pan,
        "field_20": 0,
        "field_12": 1,
    }


def _note_entry_raw(
    track_index: int,
    note: Note,
    ticks_per_beat: int,
    beats_per_bar: int,
) -> AnyDict:
    end_pos = note.start_pos + note.length
    lyric_char = ord(note.lyric[0]) if note.lyric else 0
    return {
        "track_index": track_index,
        "packed_start": _linear_to_packed(note.start_pos, ticks_per_beat, beats_per_bar),
        "packed_end": _linear_to_packed(end_pos, ticks_per_beat, beats_per_bar),
        "note_number": note.key_number,
        "lyric_char": lyric_char,
        "params": {
            "velocity": DEFAULT_VELOCITY,
            "zero": 0,
            "vibrato": 0,
            "intensity_envelope": [],
            "vibrato_envelope_1": [],
            "vibrato_envelope_0": [],
            "tail_word_0": 0,
            "tail_byte_0": 0,
            "tail_byte_1": 0,
            "tail_byte_2": 0,
            "intensity": 0,
            "param_6": 0,
            "param_17": 0,
            "tail_word_1": 0,
        },
        "lyrics": note.lyric,
        "flags": 0,
        "flags2": 0,
    }


def _make_effect_block(
    track_index: int, effect_type: int, flag: int, entries: list[AnyDict]
) -> AnyDict:
    return {
        "track_index": track_index,
        "effect_type": effect_type,
        "entries": entries,
        "flag": flag,
    }


def _default_effect_blocks(
    track_index: int, pit_entries: list[AnyDict] | None = None
) -> list[AnyDict]:
    blocks: list[AnyDict] = []
    for etype in EFFECT_TYPES_ORDER:
        flag, default_val = EFFECT_DEFAULTS[etype]
        if etype == EFFECT_TYPE_PIT and pit_entries is not None:
            blocks.append(_make_effect_block(track_index, etype, 1, pit_entries))
        elif flag and default_val is not None:
            blocks.append(
                _make_effect_block(
                    track_index,
                    etype,
                    flag,
                    [
                        {"packed_value": 0, "bypass": default_val},
                    ],
                )
            )
        else:
            blocks.append(_make_effect_block(track_index, etype, flag, []))
    return blocks


@dataclasses.dataclass
class VspGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> AnyDict:
        if project.time_signature_list:
            numerator = project.time_signature_list[0].numerator
            denominator = project.time_signature_list[0].denominator
        else:
            numerator = 4
            denominator = 4
        ticks_per_beat = TICKS_IN_WHOLE_NOTE // denominator
        first_bar_length = (
            round(project.time_signature_list[0].bar_length())
            if project.time_signature_list
            else TICKS_IN_BEAT * 4
        )
        synchronizer = TimeSynchronizer(project.song_tempo_list)

        track_entries_raw: list[AnyDict] = []
        note_entries_raw: list[AnyDict] = []
        effect_blocks: list[AnyDict] = []
        max_bar = 0
        singing_track_idx = 0

        for track in project.track_list:
            if not isinstance(track, SingingTrack):
                continue
            volume = round(track.volume * 100)
            pan = round(track.pan * 50 + 50)
            track_entries_raw.append(
                _track_dict(
                    track.title,
                    track.ai_singer_name or self.options.default_singer_name,
                    volume=max(0, min(100, volume)),
                    pan=max(0, min(100, pan)),
                )
            )
            for note in track.note_list:
                entry = _note_entry_raw(singing_track_idx, note, ticks_per_beat, numerator)
                note_entries_raw.append(entry)
                end_bar = entry["packed_end"]["high"]
                if end_bar > max_bar:
                    max_bar = end_bar

            pit_entries = None
            if track.note_list:
                pit_entries = self._generate_pitch(
                    track,
                    project.time_signature_list,
                    first_bar_length,
                    synchronizer,
                    ticks_per_beat,
                    numerator,
                )

            effect_blocks.extend(_default_effect_blocks(singing_track_idx, pit_entries))
            singing_track_idx += 1

        effect_blocks.extend(_default_effect_blocks(MASTER_TRACK_INDEX))
        effect_blocks.extend(_default_effect_blocks(EFFECT_TRACK_INDEX))

        return {
            "metadata": {
                "data": {
                    "file_size": 0,
                    "is_vocalina2": 1,
                    "is_vocalina2_pro": 11,
                    "is_trial": 0,
                    "project_name": "Imported",
                }
            },
            "tempos": {
                "data": [
                    {"tick": tempo.position, "tempo_value": round(tempo.bpm)}
                    for tempo in project.song_tempo_list
                ]
            },
            "time_signatures": {
                "data": [
                    {
                        "tick": ts.bar_index,
                        "numerator": ts.numerator,
                        "denominator": ts.denominator,
                    }
                    for ts in project.time_signature_list
                ]
            },
            "tracks": {
                "data": {
                    "tracks": track_entries_raw,
                    "is_muted": 0,
                    "master_track": _track_dict("Master", ""),
                    "effect_track": _track_dict("Effect", ""),
                }
            },
            "notes": {
                "data": {
                    "total_measures": max(max_bar + 4, DEFAULT_TOTAL_MEASURES),
                    "notes": note_entries_raw,
                }
            },
            "effects": {"data": {"blocks": effect_blocks}},
            "vst_plugins": {"data": {"blocks": []}},
            "bgm": {
                "data": {
                    "block_size": 0,
                    "is_bgm_enabled": 0,
                    "unknown_byte_0": 0,
                    "unknown_word_2": 0,
                    "unknown_int_0": 0,
                    "unknown_byte_v6": 0,
                    "unknown_word_2b": 0,
                    "raw_data": b"",
                }
            },
            "config": {
                "data": {
                    "grid": {
                        "grid_resolution1": 4,
                        "grid_snap1": 1,
                        "grid_resolution2": 4,
                        "grid_snap2": 1,
                    },
                    "playback": {
                        "playback_enabled": 1,
                        "playback_start": {
                            "low": 0,
                            "mid": 0,
                            "high": 0,
                        },
                        "playback_end": {
                            "low": 0,
                            "mid": 0,
                            "high": 0,
                        },
                        "loop_start_tick": 0,
                        "loop_end_tick": 0,
                        "loop_count": 0,
                    },
                    "volume": {
                        "volume_percent": 100,
                        "master_volume": 100,
                    },
                }
            },
        }

    @staticmethod
    def _generate_pitch(
        track: SingingTrack,
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        synchronizer: TimeSynchronizer,
        ticks_per_beat: int,
        beats_per_bar: int,
    ) -> list[AnyDict] | None:
        if not track.edited_params.pitch.points.root:
            return None

        handler = VocaloidPitchHandler(
            synchronizer=synchronizer,
            note_list=track.note_list,
            time_signature_list=time_signatures,
            first_bar_length=first_bar_length,
        )
        result = handler.from_absolute_pitch(track.edited_params.pitch)
        if result.is_empty():
            return None

        entries: list[AnyDict] = []
        prev_value = -1
        for event in result.pit.events:
            vsp_value = _vocaloid_pit_to_vsp(event.value)
            if vsp_value == prev_value:
                continue
            packed_raw = _linear_to_packed_raw(event.pos, ticks_per_beat, beats_per_bar)
            entries.append(
                {
                    "packed_value": packed_raw,
                    "bypass": vsp_value,
                }
            )
            prev_value = vsp_value

        if len(entries) > MAX_EFFECT_ENTRIES:
            step = len(entries) // MAX_EFFECT_ENTRIES + 1
            kept = [entries[0]]
            kept.extend(
                entries[i]
                for i in range(1, len(entries) - 1)
                if i % step == 0 or entries[i]["bypass"] != entries[i - 1]["bypass"]
            )
            kept.append(entries[-1])
            entries = kept

        return entries if entries else None
