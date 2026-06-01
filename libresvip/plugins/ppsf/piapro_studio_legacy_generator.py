import dataclasses
from typing import Any

from construct import Byte, Construct, Int16ul, Int32ul, PascalString, Struct

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    TimeSignature,
)
from libresvip.model.vocaloid.pitch_handler import VocaloidPitchHandler

from . import template_builder
from .legacy_model import (
    V3_PARAM_PBS_INDEX,
    V3_PARAM_PIT_INDEX,
    PpsfAudioDeviceTrackData,
    PpsfAutomationClip,
    PpsfAutomationEvent,
    PpsfClips,
    PpsfConfig,
    PpsfDevices,
    PpsfEditorClipData,
    PpsfEditorData,
    PpsfEditorDatas,
    PpsfEditorNoteData,
    PpsfEvent,
    PpsfEventControlPluginBody,
    PpsfLegacyProject,
    PpsfMusicalParamTrackData,
    PpsfPlugins,
    PpsfProject,
    PpsfTrack,
    PpsfTracks,
    PpsfTransport,
    PpsfV3SynthPluginBody,
    PpsfVocaloid3EventTrackData,
    PpsfVocaloid3NoteClip,
    PpsfVocaloid3NoteEvent,
    PpsfVocaloidEVECData,
    PpsfVSQSyllableData,
    _parse_version,
    ppsf_prefixed_array,
)
from .options import OutputOptions

VERSION_STRING = "2.0.0"
VERSION_TUPLE = _parse_version(VERSION_STRING)
VERSION_CTX = {"version": VERSION_TUPLE}

MAX_PIT_ENTRIES = 8000

DEFAULT_VIBRATO_DEPTH_DATA = bytes.fromhex(
    "0f0000000000000000000000000000007f000000010000000000000098c0be000000000000000000000000000f0000000f000000000000000000000000000000000000000000000007000000000000000000000000000000000000000000000007000000000000000100000000000000000000007f00000001000000000000"
)


def _build_bytes(struct_def: Construct, data_dict: Any) -> bytes:
    return struct_def.build(data_dict, **VERSION_CTX)


def _build_size(struct_def: Construct, data_dict: Any) -> int:
    return len(_build_bytes(struct_def, data_dict))


def _default_vibrato() -> dict:
    return {
        "handle_id": 0,
        "depth_data": b"normal",
        "flag": 0,
        "rate_data": b"",
        "start_position": 0,
        "amplitude_bp": [{"value": 64, "position": 0}],
        "frequency_bp": [{"value": 50, "position": 0}],
    }


def _bar_index_to_tick(
    time_signatures: list[TimeSignature],
) -> list[int]:
    ticks: list[int] = []
    current_tick = 0
    for i, ts in enumerate(time_signatures):
        if i == 0:
            ticks.append(0)
        else:
            prev_ts = time_signatures[i - 1]
            bar_diff = ts.bar_index - prev_ts.bar_index
            current_tick += bar_diff * round(prev_ts.bar_length())
            ticks.append(current_tick)
    return ticks


def _calculate_all_sizes(tpl: dict) -> None:
    for chunk in tpl["chunks"]:
        match chunk["magic"]:
            case "Info":
                chunk["size"] = 1
            case "Project":
                chunk["size"] = _build_size(PpsfProject, chunk["data"])
            case "Transport":
                chunk["size"] = _build_size(PpsfTransport, chunk["data"])
            case "Config":
                chunk["size"] = _build_size(PpsfConfig, chunk["data"])
            case "Devices":
                chunk["size"] = _build_size(PpsfDevices, chunk["data"])
            case "Tracks":
                for track_list_name in [
                    "audio_event_tracks",
                    "midi_event_tracks",
                    "vocaloid2_event_tracks",
                    "vocaloid3_event_tracks",
                    "midi_in_device_tracks",
                    "midi_out_device_tracks",
                    "audio_in_device_tracks",
                    "audio_out_device_tracks",
                    "audio_send_tracks",
                    "musical_param_tracks",
                ]:
                    track_list = chunk["data"][track_list_name]
                    if track_list["data"]:
                        for track in track_list["data"]:
                            if track["magic"] == "Vocaloid3EventTrack":
                                track["size"] = (
                                    _build_size(PpsfVocaloid3EventTrackData, track["data"]) + 2
                                )
                            elif track["magic"] == "AudioOutDeviceTrack":
                                track["size"] = (
                                    _build_size(PpsfAudioDeviceTrackData, track["data"]) + 2
                                )
                            elif track["magic"] == "MusicalParamTrack":
                                track["size"] = (
                                    _build_size(PpsfMusicalParamTrackData, track["data"]) + 2
                                )
                        track_list["size"] = len(
                            _build_bytes(ppsf_prefixed_array(PpsfTrack), list(track_list["data"]))
                        )
                    else:
                        track_list["size"] = 1
                chunk["size"] = _build_size(PpsfTracks, chunk["data"])
            case "Clips":
                for clip in chunk["data"]["automation_clips"]:
                    clip["size"] = _build_size(PpsfAutomationClip, clip["data"]) + 2
                chunk["size"] = _build_size(PpsfClips, chunk["data"])
            case "Events":
                if len(chunk["data"]) == 0:
                    chunk["size"] = 2
                else:
                    base_size = len(_build_bytes(ppsf_prefixed_array(PpsfEvent), chunk["data"]))
                    chunk["size"] = base_size + 1
            case "Plugins":
                for plugin_list_name in [
                    "audio_event_control_plugins",
                    "midi_event_control_plugins",
                    "vsq_event_control_plugins",
                    "vocaloid3_event_control_plugins",
                    "music_param_event_control_plugins",
                ]:
                    if plugin_list_name in chunk["data"]:
                        for plugin in chunk["data"][plugin_list_name]:
                            plugin["size"] = (
                                _build_size(PpsfEventControlPluginBody, plugin["data"]) + 2
                            )

                for plugin_list_name in [
                    "synth_event_control_plugins",
                    "vocaloid3_synth_event_control_plugins",
                ]:
                    if plugin_list_name in chunk["data"]:
                        for plugin in chunk["data"][plugin_list_name]:
                            plugin["size"] = _build_size(PpsfV3SynthPluginBody, plugin["data"]) + 2

                chunk["size"] = _build_size(PpsfPlugins, chunk["data"])
            case "EditorDatas":
                chunk["size"] = _build_size(PpsfEditorDatas, chunk["data"])


def _build_template_from_scratch(num_v3: int = 1, track_names: list[str] | None = None) -> dict:
    automation_clips = template_builder.build_automation_clips(num_v3=num_v3)

    audio_plugins = template_builder.build_audio_event_control_plugins(num_v3=num_v3)
    v3_plugins = template_builder.build_vocaloid3_event_control_plugins(num_v3=num_v3)
    music_plugins = template_builder.build_music_param_event_control_plugins(num_v3=num_v3)
    v3_synth_plugins = template_builder.build_vocaloid3_synth_plugins(num_v3=num_v3)

    num_audio_out = template_builder.NUM_AUDIO_OUT_TRACKS
    track_names = track_names or []

    v3_tracks = []
    for i in range(num_v3):
        block = template_builder._v3_block_base(i)
        v3_tracks.append(
            {
                "magic": "Vocaloid3EventTrack",
                "size": 0,
                "index": num_audio_out + i,
                "data": {
                    "base": {
                        "field_0": 1,
                        "flag_2": 0,
                        "v3_event_plugin_indices": [block + 3, block + 4],
                        "audio_event_plugin_indices": [block, block + 1, block + 2],
                        "field_180": 65535,
                        "synth_plugin_index": block + 5,
                        "field_184": 0,
                        "byte_188": 255,
                        "byte_189": 0,
                        "byte_190": 2,
                        "source_track_indices": [],
                        "byte_236": 0,
                        "byte_237": 255,
                        "ext_byte": 0,
                    },
                    "name": track_names[i] if i < len(track_names) else "MIKU_V4_CHINESE",
                    "clip_indices": [],
                    "data": b"",
                },
            }
        )

    audio_out_tracks = []
    for i in range(num_audio_out):
        audio_plugin_base = i * 3
        source_indices = list(range(num_audio_out, num_audio_out + num_v3)) if i == 0 else []

        audio_out_tracks.append(
            {
                "magic": "AudioOutDeviceTrack",
                "size": 0,
                "index": i,
                "data": {
                    "base": {
                        "field_0": 1,
                        "flag_2": 0,
                        "v3_event_plugin_indices": [],
                        "audio_event_plugin_indices": [
                            audio_plugin_base,
                            audio_plugin_base + 1,
                            audio_plugin_base + 2,
                        ],
                        "field_180": 65535,
                        "synth_plugin_index": 65535,
                        "field_184": 0,
                        "byte_188": 255,
                        "byte_189": 0,
                        "byte_190": 2,
                        "source_track_indices": source_indices,
                        "byte_236": 255,
                        "byte_237": 255,
                        "ext_byte": 0,
                    },
                    "device_impl": {
                        "byte_12": 3,
                        "byte_13": 4,
                        "field_16": 0,
                        "name": "VDAW Host Output",
                        "field_44": i * 2,
                    },
                    "data": b"",
                },
            }
        )

    music_base = template_builder._music_param_base(num_v3)
    musical_param_track = {
        "magic": "MusicalParamTrack",
        "size": 0,
        "index": num_audio_out + num_v3,
        "data": {
            "base": {
                "field_0": 1,
                "flag_2": 0,
                "v3_event_plugin_indices": [],
                "audio_event_plugin_indices": [],
                "field_180": 65535,
                "synth_plugin_index": 65535,
                "field_184": 0,
                "byte_188": 255,
                "byte_189": 0,
                "byte_190": 2,
                "source_track_indices": [],
                "byte_236": 255,
                "byte_237": 255,
                "ext_byte": 0,
            },
            "mp_plugin_index_1": music_base,
            "mp_plugin_index_2": music_base + 1,
            "mp_plugin_index_3": music_base + 2,
            "data": b"",
        },
    }

    tracks_data = {
        "audio_event_tracks": {"magic": "AudioEventTracks", "size": 0, "data": []},
        "midi_event_tracks": {"magic": "MidiEventTracks", "size": 0, "data": []},
        "vocaloid2_event_tracks": {"magic": "Vocaloid2EventTracks", "size": 0, "data": []},
        "vocaloid3_event_tracks": {"magic": "Vocaloid3EventTracks", "size": 0, "data": v3_tracks},
        "midi_in_device_tracks": {"magic": "MidiInDeviceTracks", "size": 0, "data": []},
        "midi_out_device_tracks": {"magic": "MidiOutDeviceTracks", "size": 0, "data": []},
        "audio_in_device_tracks": {"magic": "AudioInDeviceTracks", "size": 0, "data": []},
        "audio_out_device_tracks": {
            "magic": "AudioOutDeviceTracks",
            "size": 0,
            "data": audio_out_tracks,
        },
        "audio_send_tracks": {"magic": "AudioSendTracks", "size": 0, "data": []},
        "musical_param_tracks": {
            "magic": "MusicalParamTracks",
            "size": 0,
            "data": [musical_param_track],
        },
        "extension_data": b"\x00",
    }

    clips_data = {
        "audio_clips": [],
        "midi_note_clips": [],
        "midi_sysex_clips": [],
        "midi_meta_clips": [],
        "vsq_note_clips": [],
        "vocaloid3_note_clips": [],
        "automation_clips": automation_clips,
        "extension_data": b"\x00",
    }

    plugins_data = {
        "audio_event_control_plugins": audio_plugins,
        "midi_event_control_plugins": [],
        "vsq_event_control_plugins": [],
        "vocaloid3_event_control_plugins": v3_plugins,
        "synth_event_control_plugins": [],
        "vocaloid3_synth_event_control_plugins": v3_synth_plugins,
        "music_param_event_control_plugins": music_plugins,
        "vst_audio_plugins": [],
        "vst_midi_plugins": [],
        "vst_synth_plugins": [],
        "extension_data": b"\x00",
    }

    editor_datas = _build_editor_datas(vocaloid3_track_count=num_v3)

    tpl = {
        "version_string": VERSION_STRING,
        "chunks": [
            {
                "magic": "Info",
                "size": 1,
                "data": template_builder.INFO_DATA,
            },
            {
                "magic": "Project",
                "size": 0,
                "data": {
                    **template_builder.PROJECT_DATA,
                    "extension_array_8": list(range(num_audio_out, num_audio_out + num_v3)),
                    "extension_flags": num_audio_out + num_v3,
                },
            },
            {
                "magic": "Transport",
                "size": 0,
                "data": template_builder.TRANSPORT_DATA,
            },
            {
                "magic": "Config",
                "size": 0,
                "data": template_builder.CONFIG_DATA,
            },
            {
                "magic": "Devices",
                "size": 0,
                "data": template_builder.DEVICES_DATA,
            },
            {
                "magic": "Tracks",
                "size": 0,
                "data": tracks_data,
            },
            {
                "magic": "Clips",
                "size": 0,
                "data": clips_data,
            },
            {
                "magic": "Events",
                "size": 2,
                "data": [],
            },
            {
                "magic": "Plugins",
                "size": 0,
                "data": plugins_data,
            },
            {
                "magic": "EditorDatas",
                "size": 0,
                "data": editor_datas,
            },
        ],
    }

    _calculate_all_sizes(tpl)

    return tpl


def _build_editor_track_data(track_type: int, display_order: int) -> dict:
    if track_type == 0:
        return {
            "track_type": track_type,
            "display_order": 0,
            "total_height": 0,
            "component_height": 0,
            "track_color": 0,
            "track_height": 0,
            "selected_event_index": 0,
            "selected_clip_index": 0,
            "selected_sub_index": 0,
            "state_flags": 0,
            "track_width": 0,
            "horizontal_scroll": 0,
            "track_name": "0",
            "zoom_level": 0,
            "second_name": "0",
            "collapse_state": 0,
            "cursor_tick": 0,
            "selection_start_tick": 0,
            "selection_end_tick": 0,
            "playback_tick": 0,
            "raw_track_name": "",
            "raw_second_name": "",
            "editor_datas_1": [],
            "editor_datas_2": [],
            "editor_datas_3": [],
            "clip_datas": [],
            "event_datas": [],
        }
    else:
        return {
            "track_type": track_type,
            "display_order": display_order,
            "total_height": 64,
            "component_height": 55,
            "track_color": 55,
            "track_height": 0xFFFF,
            "selected_event_index": 0xFFFF,
            "selected_clip_index": 0x8000,
            "selected_sub_index": 0xFFFF,
            "state_flags": 3,
            "track_width": 1,
            "horizontal_scroll": 0,
            "track_name": "0",
            "zoom_level": 6,
            "second_name": "0.452778",
            "collapse_state": 0,
            "cursor_tick": 0xFFFFFFFF,
            "selection_start_tick": 0xFFFFFFFF,
            "selection_end_tick": 0xFFFFFFFF,
            "playback_tick": 0xFFFFFFFF,
            "raw_track_name": "",
            "raw_second_name": "",
            "editor_datas_1": [],
            "editor_datas_2": [],
            "editor_datas_3": [],
            "clip_datas": [],
            "event_datas": [],
        }


def _build_ecls_for_notes(notes: list[Note]) -> list[dict]:
    if not notes:
        return []

    enot_list = []
    for note_index, note in enumerate(notes):
        vsqs_data = {
            "quantize_mode": 15,
            "unknown_field_1": 4294901764,
            "unknown_field_2": 0xFFFFFFFF,
            "syllable_strings": ["", note.lyric or "la", note.pronunciation or "4 a", ""],
        }
        vsqs_size = _build_size(PpsfVSQSyllableData, vsqs_data)
        vsqs = {
            "magic": "VocalSynthQuantizeSyllable",
            "size": vsqs_size,
            "data": vsqs_data,
        }

        vsqa_entries = []
        vsqa_params = [
            ("CVV", 12),
            ("VSil", 13),
            ("CTop", 13),
            ("EndC", 13),
            ("ALT", 12),
        ]

        for type_name, expected_size in vsqa_params:
            vsqa_data = {
                "parameter_name": "-1",
                "unknown_int": 0xFFFFFFFF,
                "mode": 0,
                "type_name": type_name,
            }
            vsqa_size = _build_size(PpsfVocaloidEVECData, vsqa_data)
            vsqa = {
                "magic": "VocaloidEVECData",
                "size": vsqa_size,
                "data": vsqa_data,
            }
            vsqa_entries.append(vsqa)

        note_data = {
            "pos_tick": note.start_pos,
            "dur_tick": note.length,
            "dur_tick_copy": note.length,
            "unknown_field": 0xFFFE,
            "phoneme_flag": 4,
            "attack_flag": 0,
            "release_flag": 0,
            "vibrato_start": 0,
            "vibrato_duration": 0xFFFFFFFF,
            "sub_array_1": [vsqs],
            "int32_array": [note_index, 0xFFFFFFFF, 0xFFFFFFFF],
            "sub_array_2": vsqa_entries,
        }

        note_data_size = _build_size(PpsfEditorNoteData, note_data)

        enot = {
            "magic": "EditorNoteData",
            "size": note_data_size,
            "data": note_data,
        }
        enot_list.append(enot)

    clip_duration = 6 if notes else 0

    ecls_inner = {
        "clip_type": 0,
        "start_pos": 0,
        "duration": clip_duration,
        "track_name": "0",
        "color_index": 0,
        "x_position": 0xFFFF,
        "y_position": 0xFFFF,
        "clip_flags": 0xFFFF,
        "clip_id": 0xFFFFFFFF,
        "sub_array": [],
        "element_array": enot_list,
    }

    ecls_data_struct = Struct(
        "clip_type" / Int16ul,
        "start_pos" / Int16ul,
        "duration" / Int16ul,
        "track_name" / PascalString(Byte, "utf-8"),
        "color_index" / Int16ul,
        "x_position" / Int16ul,
        "y_position" / Int16ul,
        "clip_flags" / Int16ul,
        "clip_id" / Int32ul,
        "sub_array" / ppsf_prefixed_array(PpsfEditorData),
        "element_array" / ppsf_prefixed_array(PpsfEditorData),
    )

    ecls_inner_size = _build_size(ecls_data_struct, ecls_inner)

    ecls = {
        "magic": b"ECLS",
        "size": ecls_inner_size,
        "data": ecls_inner,
    }

    return [ecls]


def _build_editor_datas(
    vocaloid3_track_count: int,
    audio_out_track_count: int = 2,
    note_lists: list[list[Note]] | None = None,
) -> dict:
    track_data_struct = Struct(
        "track_type" / Int16ul,
        "display_order" / Int16ul,
        "total_height" / Int16ul,
        "component_height" / Int16ul,
        "track_color" / Int16ul,
        "track_height" / Int16ul,
        "selected_event_index" / Int16ul,
        "selected_clip_index" / Int16ul,
        "selected_sub_index" / Int16ul,
        "state_flags" / Int16ul,
        "track_width" / Int16ul,
        "horizontal_scroll" / Int16ul,
        "track_name" / PascalString(Byte, "utf-8"),
        "zoom_level" / Int16ul,
        "second_name" / PascalString(Byte, "utf-8"),
        "collapse_state" / Int16ul,
        "cursor_tick" / Int32ul,
        "selection_start_tick" / Int32ul,
        "selection_end_tick" / Int32ul,
        "playback_tick" / Int32ul,
        "raw_track_name" / PascalString(Byte, "utf-8"),
        "raw_second_name" / PascalString(Byte, "utf-8"),
        "editor_datas_1" / ppsf_prefixed_array(PpsfEditorData),
        "editor_datas_2" / ppsf_prefixed_array(PpsfEditorData),
        "editor_datas_3" / ppsf_prefixed_array(PpsfEditorData),
        "clip_datas" / ppsf_prefixed_array(PpsfEditorClipData),
        "event_datas" / ppsf_prefixed_array(PpsfEditorData),
    )

    track_datas = []
    note_lists = note_lists or []

    for i in range(vocaloid3_track_count):
        track_data = _build_editor_track_data(3, i)

        if i < len(note_lists) and len(note_lists[i]) > 0:
            track_data["clip_datas"] = _build_ecls_for_notes(note_lists[i])

        inner_bytes = _build_bytes(track_data_struct, track_data)
        track_datas.append(
            {
                "magic": b"ETRS",
                "size": len(inner_bytes),
                "data": track_data,
            }
        )

    for i in range(audio_out_track_count):
        track_data = _build_editor_track_data(0, i)
        inner_bytes = _build_bytes(track_data_struct, track_data)
        track_datas.append(
            {
                "magic": b"ETRS",
                "size": len(inner_bytes),
                "data": track_data,
            }
        )

    header = {
        "version_code": 0x00000100,
        "flags": 0xFFFF0004,
        "reserved_08": 0,
        "version_major": 9,
        "version_str": b"0.0433824",
        "version_minor": 1,
        "version_minor_ch": 0x30,
        "version_revision": 1,
        "version_revision_ch": 0x31,
        "editor_hscroll": 0,
        "sampling_related": 574,
        "reserved_32": 0,
        "reserved_34": 0,
        "editor_track_count": 12,
        "sentinel_42": 0xFFFFFFFF,
        "sentinel_46": 0xFFFFFFFF,
        "sentinel_50": 0xFFFFFFFF,
        "sentinel_54": 0xFFFFFFFF,
        "time_position": 0,
        "sentinel_62": 0xFFFFFFFF,
        "sentinel_66": 0xFFFFFFFF,
        "trailing_zero": 0,
        "trailing_flag": 3,
    }

    return {
        "version_flag": 0x00000101,
        "window_rect": {
            "magic": b"RECT",
            "size": 16,
            "left": 10,
            "top": 10,
            "right": 1034,
            "bottom": 778,
        },
        "header": header,
        "track_datas": track_datas,
        "footer_rect1_pad": b"\x00",
        "footer_rect1": {
            "magic": b"RECT",
            "size": 16,
            "data": b"\x00" * 16,
        },
        "footer_rect2": {
            "magic": b"RECT",
            "size": 16,
            "data": b"\x00" * 16,
        },
        "footer_rest": b"\xff\xff\xff\xff\xff\x00\xff\x00\x00\x00\x00\x00",
    }


@dataclasses.dataclass
class PiaproStudioLegacyGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> bytes:
        singing_tracks: list[SingingTrack] = [
            t for t in project.track_list if isinstance(t, SingingTrack)
        ]
        num_v3 = max(1, len(singing_tracks))
        track_names = [t.title for t in singing_tracks]
        tpl = _build_template_from_scratch(num_v3=num_v3, track_names=track_names)

        if project.time_signature_list:
            first_bar_length = round(project.time_signature_list[0].bar_length())
        else:
            first_bar_length = TICKS_IN_BEAT * 4
        synchronizer = TimeSynchronizer(project.song_tempo_list)

        events: list[dict] = []
        note_clip_dicts: list[dict] = []

        tempo_clip_idx = -1
        meter_clip_idx = -1
        pit_clip_indices: list[int] = []
        for chunk in tpl["chunks"]:
            if chunk["magic"] == "Plugins":
                for pg in chunk["data"]["music_param_event_control_plugins"]:
                    if pg["data"]["name"] == "Tempo":
                        tempo_clip_idx = pg["data"]["self_clip_idx"]
                    elif pg["data"]["name"] == "Meter":
                        meter_clip_idx = pg["data"]["self_clip_idx"]
                pit_clip_indices.extend(
                    pg["data"]["self_clip_idx"]
                    for pg in chunk["data"]["vocaloid3_event_control_plugins"]
                    if pg["data"]["name"] == "Vocaloid3 Parameter"
                )

        per_track_pit: list[tuple[list[int], list[int]]] = []
        for i, track in enumerate(singing_tracks):
            note_events = self._build_note_events(track.note_list, offset=0)
            note_start = len(events)
            events.extend(note_events)
            note_indices = list(range(note_start, len(events)))

            song_end_tick = 0
            if track.note_list:
                last_note = max(track.note_list, key=lambda n: n.start_pos + n.length)
                song_end_tick = last_note.start_pos + last_note.length

            note_clip_data = {
                "noteclip": {
                    "iclip": {
                        "field_4": 1,
                        "field_6": 1,
                        "event_indices": note_indices,
                        "name": track.title,
                        "flag": 1,
                        "extension": b"",
                    },
                    "offset": 0,
                    "field_108": 0,
                    "song_end_anchor_a": song_end_tick,
                    "field_116": 0,
                    "song_end_anchor_b": song_end_tick,
                    "field_124": 0,
                    "field_128": 0,
                    "field_132": 0,
                },
                "v3_field_156": 65535,
                "v3_field_158": 1,
                "data": b"",
            }
            size = _build_size(PpsfVocaloid3NoteClip, note_clip_data) + 2
            note_clip_dicts.append(
                {
                    "magic": "Vocaloid3NoteClip",
                    "size": size,
                    "index": i,
                    "data": note_clip_data,
                }
            )

            if track.edited_params.pitch.points.root:
                pit_idx, pbs_idx = self._build_pit_events(
                    track,
                    project.time_signature_list,
                    first_bar_length,
                    synchronizer,
                    events,
                )
            else:
                pit_idx, pbs_idx = [], []
            per_track_pit.append((pit_idx, pbs_idx))

        tempo_event_indices = self._build_tempo_events(project.song_tempo_list, events)
        meter_event_indices = self._build_meter_events(project.time_signature_list, events)

        index_offset = len(note_clip_dicts)
        pit_clip_to_track = {pit_clip_indices[i]: i for i in range(len(singing_tracks))}

        for chunk in tpl["chunks"]:
            if chunk["magic"] == "Tracks":
                for j, t in enumerate(chunk["data"]["vocaloid3_event_tracks"]["data"]):
                    new_track_data = {
                        "base": t["data"]["base"],
                        "name": t["data"]["name"],
                        "clip_indices": [j] if j < index_offset else [],
                        "data": bytes(t["data"]["data"]),
                    }
                    t["data"] = new_track_data
                    t["size"] = _build_size(PpsfVocaloid3EventTrackData, new_track_data) + 2
            elif chunk["magic"] == "Clips":
                chunk["data"]["vocaloid3_note_clips"] = note_clip_dicts

                for clip in chunk["data"]["automation_clips"]:
                    base_index = clip["index"]
                    clip["index"] = base_index + index_offset

                    if base_index == tempo_clip_idx:
                        clip["data"]["event_indices"] = tempo_event_indices
                    elif base_index == meter_clip_idx:
                        clip["data"]["event_indices"] = meter_event_indices
                    elif base_index in pit_clip_to_track:
                        track_pos = pit_clip_to_track[base_index]
                        pit_idx, pbs_idx = per_track_pit[track_pos]
                        clip["data"]["sub_event_indices"][V3_PARAM_PIT_INDEX - 1] = pit_idx
                        clip["data"]["sub_event_indices"][V3_PARAM_PBS_INDEX - 1] = pbs_idx

                for clip in chunk["data"]["automation_clips"]:
                    clip["size"] = _build_size(PpsfAutomationClip, clip["data"]) + 2
            elif chunk["magic"] == "Events":
                chunk["data"] = events

        max_tick = 0
        for track in singing_tracks:
            for note in track.note_list:
                end = note.start_pos + note.length
                if end > max_tick:
                    max_tick = end
        if max_tick > 0:
            padded = max_tick + first_bar_length * 2
            for chunk in tpl["chunks"]:
                if chunk["magic"] == "Project":
                    chunk["data"]["impl"]["project_field_12"] = max(130560, padded)
                    chunk["data"]["impl"]["project_field_16"] = max(
                        136000, padded + first_bar_length * 12
                    )
                    break

        vocaloid3_count = max(1, len(singing_tracks))

        note_lists = [track.note_list for track in singing_tracks]

        editor_datas = _build_editor_datas(vocaloid3_count, note_lists=note_lists)

        edts_found = False
        for chunk in tpl["chunks"]:
            if chunk["magic"] == "EditorDatas":
                chunk["data"] = editor_datas
                chunk["size"] = _build_size(PpsfEditorDatas, editor_datas)
                edts_found = True
                break

        if not edts_found:
            edts_size = _build_size(PpsfEditorDatas, editor_datas)
            tpl["chunks"].append(
                {
                    "magic": "EditorDatas",
                    "size": edts_size,
                    "data": editor_datas,
                }
            )

        index_offset = len(note_clip_dicts)
        if index_offset > 0:
            for chunk in tpl["chunks"]:
                if chunk["magic"] == "Plugins":
                    for plugin_list_name in [
                        "audio_event_control_plugins",
                        "midi_event_control_plugins",
                        "vsq_event_control_plugins",
                        "vocaloid3_event_control_plugins",
                        "synth_event_control_plugins",
                        "vocaloid3_synth_event_control_plugins",
                        "music_param_event_control_plugins",
                    ]:
                        if plugin_list_name in chunk["data"]:
                            for plugin in chunk["data"][plugin_list_name]:
                                if "self_clip_idx" in plugin.get("data", {}):
                                    plugin["data"]["self_clip_idx"] += index_offset

        for chunk in tpl["chunks"]:
            match chunk["magic"]:
                case "Info":
                    chunk["size"] = 1
                case "Project":
                    chunk["size"] = _build_size(PpsfProject, chunk["data"])
                case "Transport":
                    chunk["size"] = _build_size(PpsfTransport, chunk["data"])
                case "Config":
                    chunk["size"] = _build_size(PpsfConfig, chunk["data"])
                case "Devices":
                    chunk["size"] = _build_size(PpsfDevices, chunk["data"])
                case "Clips":
                    chunk["size"] = _build_size(PpsfClips, chunk["data"])
                case "Events":
                    base_size = len(_build_bytes(ppsf_prefixed_array(PpsfEvent), events))
                    chunk["size"] = base_size + 1
                case "Tracks":
                    for track_list_name in [
                        "audio_event_tracks",
                        "midi_event_tracks",
                        "vocaloid2_event_tracks",
                        "vocaloid3_event_tracks",
                        "midi_in_device_tracks",
                        "midi_out_device_tracks",
                        "audio_in_device_tracks",
                        "audio_out_device_tracks",
                        "audio_send_tracks",
                        "musical_param_tracks",
                    ]:
                        track_list = chunk["data"][track_list_name]
                        if track_list["data"]:
                            for track in track_list["data"]:
                                if track["magic"] == "Vocaloid3EventTrack":
                                    track["size"] = (
                                        _build_size(PpsfVocaloid3EventTrackData, track["data"]) + 2
                                    )
                                elif track["magic"] == "AudioOutDeviceTrack":
                                    track["size"] = (
                                        _build_size(PpsfAudioDeviceTrackData, track["data"]) + 2
                                    )
                                elif track["magic"] == "MusicalParamTrack":
                                    track["size"] = (
                                        _build_size(PpsfMusicalParamTrackData, track["data"]) + 2
                                    )
                            track_list["size"] = len(
                                _build_bytes(
                                    ppsf_prefixed_array(PpsfTrack), list(track_list["data"])
                                )
                            )
                        else:
                            track_list["size"] = 1
                    chunk["size"] = _build_size(PpsfTracks, chunk["data"])
                case "Plugins":
                    for plugin_list_name in [
                        "audio_event_control_plugins",
                        "midi_event_control_plugins",
                        "vsq_event_control_plugins",
                        "vocaloid3_event_control_plugins",
                        "music_param_event_control_plugins",
                    ]:
                        if plugin_list_name in chunk["data"]:
                            for plugin in chunk["data"][plugin_list_name]:
                                plugin["size"] = (
                                    _build_size(PpsfEventControlPluginBody, plugin["data"]) + 2
                                )

                    for plugin_list_name in [
                        "synth_event_control_plugins",
                        "vocaloid3_synth_event_control_plugins",
                    ]:
                        if plugin_list_name in chunk["data"]:
                            for plugin in chunk["data"][plugin_list_name]:
                                plugin["size"] = (
                                    _build_size(PpsfV3SynthPluginBody, plugin["data"]) + 2
                                )

                    chunk["size"] = _build_size(PpsfPlugins, chunk["data"])

        return PpsfLegacyProject.build(tpl)

    @staticmethod
    def _build_note_events(notes: list[Note], offset: int) -> list[dict]:
        result = []
        for note in notes:
            data = {
                "tick": note.start_pos - offset,
                "note": note.key_number,
                "duration": note.length,
                "velocity": 64,
                "byte_25": 0,
                "byte_26": 0,
                "byte_27": 0,
                "byte_28": 50,
                "byte_29": 50,
                "byte_30": 127,
                "lyric": note.lyric or "la",
                "protected": 0,
                "phoneme": note.pronunciation or "4 a",
                "vibrato": {
                    "handle_id": 0,
                    "depth_data": DEFAULT_VIBRATO_DEPTH_DATA,
                    "flag": 0,
                    "rate_data": b"",
                    "start_position": 0,
                    "amplitude_bp": [],
                    "frequency_bp": [],
                },
                "trailing": 0,
            }
            size = _build_size(PpsfVocaloid3NoteEvent, data)
            result.append(
                {
                    "magic": "Vocaloid3NoteEvent",
                    "size": size,
                    "data": data,
                }
            )
        return result

    @staticmethod
    def _build_tempo_events(tempos: list, events: list[dict]) -> list[int]:
        indices = []

        if len(tempos) == 1 and tempos[0].position == 0 and abs(tempos[0].bpm - 120.0) < 0.01:
            return indices

        for tempo in tempos:
            data = {
                "tick": tempo.position,
                "value": round(tempo.bpm * 10000),
                "interpolation_type": 0,
            }
            size = _build_size(PpsfAutomationEvent, data)
            indices.append(len(events))
            events.append(
                {
                    "magic": "AutomationEvent",
                    "size": size,
                    "data": data,
                }
            )
        return indices

    @staticmethod
    def _build_meter_events(time_signatures: list[TimeSignature], events: list[dict]) -> list[int]:
        indices = []

        if (
            len(time_signatures) == 1
            and time_signatures[0].bar_index == 0
            and time_signatures[0].numerator == 4
            and time_signatures[0].denominator == 4
        ):
            return indices

        ticks = _bar_index_to_tick(time_signatures)
        indices = []
        for ts, tick in zip(time_signatures, ticks):
            value = (ts.numerator << 8) | ts.denominator
            data = {
                "tick": tick,
                "value": value,
                "interpolation_type": 0,
            }
            size = _build_size(PpsfAutomationEvent, data)
            indices.append(len(events))
            events.append(
                {
                    "magic": "AutomationEvent",
                    "size": size,
                    "data": data,
                }
            )
        return indices

    def _build_pit_events(
        self,
        track: SingingTrack,
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        synchronizer: TimeSynchronizer,
        events: list[dict],
    ) -> tuple[list[int], list[int]]:
        handler = VocaloidPitchHandler(
            synchronizer=synchronizer,
            note_list=track.note_list,
            time_signature_list=time_signatures,
            first_bar_length=first_bar_length,
        )
        result = handler.from_absolute_pitch(track.edited_params.pitch)
        if result.is_empty():
            return [], []

        pit_indices: list[int] = []
        pending: list[dict] = []
        for pit_event in result.pit.events:
            value = pit_event.value
            if value < 0:
                value += 0x100000000
            data = {
                "tick": pit_event.pos,
                "value": value,
                "interpolation_type": 0,
            }
            size = _build_size(PpsfAutomationEvent, data)
            pending.append({"magic": "AutomationEvent", "size": size, "data": data})

        if len(pending) > MAX_PIT_ENTRIES:
            step = len(pending) // MAX_PIT_ENTRIES + 1
            kept = [pending[0]]
            kept.extend(
                pending[i]
                for i in range(1, len(pending) - 1)
                if i % step == 0 or pending[i]["data"]["value"] != pending[i - 1]["data"]["value"]
            )
            kept.append(pending[-1])
            pending = kept

        for ev in pending:
            pit_indices.append(len(events))
            events.append(ev)

        pbs_indices: list[int] = []
        for pbs_event in result.pbs.events:
            data = {
                "tick": pbs_event.pos,
                "value": pbs_event.value,
                "interpolation_type": 0,
            }
            size = _build_size(PpsfAutomationEvent, data)
            pbs_indices.append(len(events))
            events.append({"magic": "AutomationEvent", "size": size, "data": data})

        return pit_indices, pbs_indices
