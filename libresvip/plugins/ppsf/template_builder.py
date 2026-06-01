# Audio Mixer plugin (index 0)
AUDIO_MIXER_PLUGIN = {
    "name": "Audio Mixer",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 2,
    "parameters": [{"value": 4000, "marker": 1}, {"value": 0, "marker": 1}],
    "self_clip_idx": 1,
    "vfxc_blob": {"data": bytes.fromhex("0000000000010000000200000000000000a00f000000000000")},
    "trailing": b"\x00",
}

# Audio Send plugin (index 1)
AUDIO_SEND_PLUGIN = {
    "name": "Audio Send",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 8,
    "parameters": [{"value": 0, "marker": 1}] * 8,
    "self_clip_idx": 1,
    "vfxc_blob": {
        "data": bytes.fromhex(
            "00000000000100000008000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
    },
    "trailing": b"\x00",
}

# Audio Eq plugin (index 2)
AUDIO_EQ_PLUGIN = {
    "name": "Audio Eq",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 10,
    "parameters": [
        {"value": 1000, "marker": 1},
        {"value": 20, "marker": 1},
        {"value": 4000, "marker": 1},
        {"value": 10000, "marker": 1},
        {"value": 1000, "marker": 1},
        {"value": 1000, "marker": 1},
        {"value": 1000, "marker": 1},
        {"value": 500, "marker": 1},
        {"value": 500, "marker": 1},
        {"value": 500, "marker": 1},
    ],
    "self_clip_idx": 3,
    "vfxc_blob": {
        "data": bytes.fromhex(
            "0000000000010000000a00000000000000e803000014000000a00f000010270000e8030000e8030000e8030000f4010000f4010000f4010000"
        )
    },
    "trailing": b"\x00",
}

# Vocaloid3 Parameter plugin
V3_PARAM_PLUGIN = {
    "name": "Vocaloid3 Parameter",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 11,
    "parameters": [
        {"value": 64, "marker": 1},
        {"value": 0, "marker": 1},
        {"value": 64, "marker": 1},
        {"value": 0, "marker": 1},
        {"value": 64, "marker": 1},
        {"value": 64, "marker": 1},
        {"value": 0, "marker": 1},
        {"value": 1, "marker": 1},
        {"value": 0, "marker": 1},
        {"value": 0, "marker": 1},
        {"value": 0, "marker": 1},
    ],
    "self_clip_idx": 51,
    "vfxc_blob": {
        "data": bytes.fromhex(
            "0000000000010000000b000000000000004000000000000000400000000000000040000000400000000000000001000000000000000000000000000000"
        )
    },
    "trailing": b"\x00\x00\x00\x00\x00",
}

# Vocaloid3 Program Change plugin
V3_PROG_CHANGE_PLUGIN = {
    "name": "Vocaloid3 Program Change",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 1,
    "parameters": [{"value": 0, "marker": 0}],
    "self_clip_idx": 52,
    "vfxc_blob": {"data": bytes.fromhex("000000000001000000010000000000000000000000")},
    "trailing": b"\x00\x00\x00\x00\x00",
}

# VOCALOID3 Synth plugin (index 53)
V3_SYNTH_PLUGIN = {
    "name": "VOCALOID3",
    "required_tag": "required",
    "data": b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00L\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x10'\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x005\x00\x82IvfxcA\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10'\x00\x00\x10'\x00\x00\x10'\x00\x00\x10'\x00\x00\x10'\x00\x00\x10'\x00\x00\x10'\x00\x00\x10'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
}

# Tempo plugin
TEMPO_PLUGIN = {
    "name": "Tempo",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 1,
    "parameters": [{"value": 1200000, "marker": 1}],
    "self_clip_idx": 54,
    "vfxc_blob": {"data": bytes.fromhex("0000000000010000000100000000000000804f1200")},
    "trailing": b"\x00",
}

# Key plugin
KEY_PLUGIN = {
    "name": "Key",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 1,
    "parameters": [{"value": 64, "marker": 0}],
    "self_clip_idx": 55,
    "vfxc_blob": {"data": bytes.fromhex("000000000001000000010000000000000040000000")},
    "trailing": b"\x00",
}

# Meter plugin
METER_PLUGIN = {
    "name": "Meter",
    "reserved": b"\x00" * 10,
    "flag": 1,
    "param_count": 1,
    "parameters": [{"value": 1028, "marker": 1}],
    "self_clip_idx": 56,
    "vfxc_blob": {"data": bytes.fromhex("000000000001000000010000000000000004040000")},
    "trailing": b"\x00",
}

INFO_DATA = ""

PROJECT_DATA = {
    "impl": {
        "project_field_12": 130560,
        "project_field_16": 136000,
        "project_field_20": 0,
        "project_field_24": 0,
        "project_field_28": 126720,
        "project_field_32": 1,
        "project_field_36": 0,
        "project_field_40": 0,
        "vocaloid2_singers": [],
        "vocaloid3_singers": [
            {
                "singer_id": "MIKU_V4_CHINESE",
                "singer_name": "MIKU_V4_Chinese",
                "unknown1": 0,
                "unknown2": 4,
                "voice_setting": {
                    "name": "BNGE7CP7EMTRSNC3",
                    "parameters": {
                        "param1": 0,
                        "param2": 0,
                        "param3": 0,
                        "param4": 0,
                        "param5": 0,
                    },
                },
                "has_extra_voice_setting": 0,
                "extra_voice_setting": None,
            }
        ],
    },
    "extension_array_1": [],
    "extension_array_2": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "extension_array_3": [],
    "extension_array_4": [],
    "extension_array_5": [],
    "extension_array_6": [],
    "extension_array_7": [],
    "extension_array_8": [],
    "extension_array_9": [],
    "extension_flags": 16,
    "extension_data": b"\x00",
}

TRANSPORT_DATA = {"transport_value": 0, "transport_flags": 0}

CONFIG_DATA = {"config_value_1": 0, "config_value_2": 0, "config_flags": 0}

DEVICES_DATA = {
    "subcomponent_array_1": {"size": 0, "subcomponents": []},
    "subcomponent_array_2": {"size": 0, "subcomponents": []},
    "subcomponent_array_3": {"size": 0, "subcomponents": []},
    "subcomponent_array_4": {"size": 0, "subcomponents": []},
    "subcomponent_array_5": {"size": 0, "subcomponents": []},
    "device_field_1": 0,
    "device_field_2": 0,
    "device_field_3": 32,
}


def build_audio_mixer_plugin(clip_idx: int) -> dict:
    data = dict(AUDIO_MIXER_PLUGIN)
    data["self_clip_idx"] = clip_idx

    return {
        "magic": "AudioEventControlPlugin",
        "size": 0,
        "data": data,
    }


def build_audio_send_plugin(clip_idx: int) -> dict:
    data = dict(AUDIO_SEND_PLUGIN)
    data["self_clip_idx"] = clip_idx
    return {
        "magic": "AudioEventControlPlugin",
        "size": 0,
        "data": data,
    }


def build_audio_eq_plugin(clip_idx: int) -> dict:
    data = dict(AUDIO_EQ_PLUGIN)
    data["self_clip_idx"] = clip_idx
    return {
        "magic": "AudioEventControlPlugin",
        "size": 0,
        "data": data,
    }


def build_automation_clip(index: int, field_4: int, field_6: int) -> dict:
    return {
        "magic": "AutomationClip",
        "size": 0,
        "index": index,
        "data": {
            "field_4": field_4,
            "field_6": field_6,
            "event_indices": [],
            "sub_event_indices": [[] for _ in range(field_4 - 1)],
            "padding": 0,
            "marker": 1,
            "plugin_index": index,
        },
    }


NUM_AUDIO_OUT_TRACKS = 16


def _v3_block_base(track_idx: int) -> int:
    return NUM_AUDIO_OUT_TRACKS * 3 + track_idx * 6


def _music_param_base(num_v3: int) -> int:
    return NUM_AUDIO_OUT_TRACKS * 3 + num_v3 * 6


def build_audio_event_control_plugins(num_v3: int = 1) -> list[dict]:
    plugins = []

    def add_triplet(base: int) -> None:
        mixer = build_audio_mixer_plugin(base)
        mixer["index"] = base
        plugins.append(mixer)
        send = build_audio_send_plugin(base + 1)
        send["index"] = base + 1
        plugins.append(send)
        eq = build_audio_eq_plugin(base + 2)
        eq["index"] = base + 2
        plugins.append(eq)

    for track_idx in range(NUM_AUDIO_OUT_TRACKS):
        add_triplet(track_idx * 3)
    for i in range(num_v3):
        add_triplet(_v3_block_base(i))

    return plugins


def build_automation_clips(num_v3: int = 1) -> list[dict]:
    clips = []

    for track_idx in range(NUM_AUDIO_OUT_TRACKS):
        base_idx = track_idx * 3
        clips.append(build_automation_clip(base_idx, 2, 2))
        clips.append(build_automation_clip(base_idx + 1, 8, 8))
        clips.append(build_automation_clip(base_idx + 2, 10, 10))

    for i in range(num_v3):
        base_idx = _v3_block_base(i)
        clips.append(build_automation_clip(base_idx, 2, 2))
        clips.append(build_automation_clip(base_idx + 1, 8, 8))
        clips.append(build_automation_clip(base_idx + 2, 10, 10))
        clips.append(build_automation_clip(base_idx + 3, 11, 11))
        clips.append(build_automation_clip(base_idx + 4, 1, 1))
        clips.append(build_automation_clip(base_idx + 5, 76, 76))

    base_idx = _music_param_base(num_v3)
    clips.append(build_automation_clip(base_idx, 1, 1))
    clips.append(build_automation_clip(base_idx + 1, 1, 1))
    clips.append(build_automation_clip(base_idx + 2, 1, 1))

    return clips


def _build_v3_param_plugin(index: int) -> dict:
    return {
        "magic": "Vocaloid3EventControlPlugin",
        "size": 0,
        "index": index,
        "data": {
            "name": "Vocaloid3 Parameter",
            "reserved": b"\x00" * 10,
            "flag": 1,
            "param_count": 11,
            "parameters": [
                {"value": 64, "marker": 1},
                {"value": 0, "marker": 1},
                {"value": 64, "marker": 1},
                {"value": 0, "marker": 1},
                {"value": 64, "marker": 1},
                {"value": 64, "marker": 1},
                {"value": 0, "marker": 1},
                {"value": 1, "marker": 1},
                {"value": 0, "marker": 1},
                {"value": 0, "marker": 1},
                {"value": 0, "marker": 1},
            ],
            "self_clip_idx": index,
            "vfxc_blob": {
                "data": bytes.fromhex(
                    "0000000000010000000b000000000000004000000000000000400000000000000040000000400000000000000001000000000000000000000000000000"
                )
            },
            "trailing": b"\x00\x00\x00\x00\x00",
        },
    }


def _build_v3_prog_change_plugin(index: int) -> dict:
    return {
        "magic": "Vocaloid3EventControlPlugin",
        "size": 0,
        "index": index,
        "data": {
            "name": "Vocaloid3 Program Change",
            "reserved": b"\x00" * 10,
            "flag": 1,
            "param_count": 1,
            "parameters": [
                {"value": 0, "marker": 0},
            ],
            "self_clip_idx": index,
            "vfxc_blob": {"data": bytes.fromhex("000000000001000000010000000000000000000000")},
            "trailing": b"\x00\x00\x00\x00\x00",
        },
    }


def build_vocaloid3_event_control_plugins(num_v3: int = 1) -> list[dict]:
    plugins = []
    for i in range(num_v3):
        base = _v3_block_base(i)
        plugins.append(_build_v3_param_plugin(base + 3))
        plugins.append(_build_v3_prog_change_plugin(base + 4))
    return plugins


def build_music_param_event_control_plugins(num_v3: int = 1) -> list[dict]:
    base_clip_idx = _music_param_base(num_v3)
    return [
        {
            "magic": "MusicParamEventControlPlugin",
            "size": 0,
            "index": base_clip_idx,
            "data": {
                "name": "Tempo",
                "reserved": b"\x00" * 10,
                "flag": 1,
                "param_count": 1,
                "parameters": [
                    {"value": 1200000, "marker": 1},
                ],
                "self_clip_idx": base_clip_idx,
                "vfxc_blob": {"data": bytes.fromhex("0000000000010000000100000000000000804f1200")},
                "trailing": b"\x00",
            },
        },
        {
            "magic": "MusicParamEventControlPlugin",
            "size": 0,
            "index": base_clip_idx + 1,
            "data": {
                "name": "Key",
                "reserved": b"\x00" * 10,
                "flag": 1,
                "param_count": 1,
                "parameters": [
                    {"value": 64, "marker": 0},
                ],
                "self_clip_idx": base_clip_idx + 1,
                "vfxc_blob": {"data": bytes.fromhex("000000000001000000010000000000000040000000")},
                "trailing": b"\x00",
            },
        },
        {
            "magic": "MusicParamEventControlPlugin",
            "size": 0,
            "index": base_clip_idx + 2,
            "data": {
                "name": "Meter",
                "reserved": b"\x00" * 10,
                "flag": 1,
                "param_count": 1,
                "parameters": [
                    {"value": 1028, "marker": 1},
                ],
                "self_clip_idx": base_clip_idx + 2,
                "vfxc_blob": {"data": bytes.fromhex("000000000001000000010000000000000004040000")},
                "trailing": b"\x00",
            },
        },
    ]


def build_vocaloid3_synth_plugins(num_v3: int = 1) -> list[dict]:
    return [
        {
            "magic": "Vocaloid3SynthEventControlPlugin",
            "size": 0,
            "index": _v3_block_base(i) + 5,
            "data": dict(V3_SYNTH_PLUGIN),
        }
        for i in range(num_v3)
    ]
