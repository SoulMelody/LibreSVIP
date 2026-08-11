import json
import pathlib
from itertools import pairwise

from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature
from libresvip.model.point import Point
from libresvip.plugins.ace.ace_converter import AceMobileConverter
from libresvip.plugins.ace.model import AceProject
from libresvip.plugins.acep.ace_studio_generator import AceGenerator
from libresvip.plugins.acep.options import OutputOptions as AcepOutputOptions


def test_ace_mobile_plugin_metadata() -> None:
    assert AceMobileConverter._alias_ == "ace"
    assert AceMobileConverter.info.suffixes == ("ace",)


def test_ace_mobile_loads_legacy_root_notes(tmp_path: pathlib.Path) -> None:
    ace_path = tmp_path / "legacy.ace"
    ace_path.write_text(
        json.dumps(
            {
                "debugInfo": {"platform": "android"},
                "song_info": {"bpm": 120, "beat_of_bar": 4},
                "bgm_info": {"tracks": [{"bpm": 90}]},
                "role_info": {"name": "singer", "role_id": 2},
                "setting": {"singer_volume": 0.75},
                "tracks": None,
                "notes": [
                    {
                        "start_time": 1.0,
                        "end_time": 2.0,
                        "pitch": 60,
                        "word": "\u00b3\u00b0",
                        "pinyin": "chao",
                        "pitchBends": [
                            {"time": 1.0, "pitch": 0.0},
                            {"time": 1.5, "pitch": 0.5},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    project = AceMobileConverter.load(
        ace_path,
        {"import_instrumental_track": False},
    )

    assert project.song_tempo_list[0].bpm == 90
    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert track.title == "singer"
    assert track.volume == 0.75
    assert len(track.note_list) == 1
    note = track.note_list[0]
    assert (note.start_pos, note.length, note.key_number) == (720, 720, 48)
    assert (note.lyric, note.pronunciation) == ("chao", None)
    assert Point(3000, 4850) in track.edited_params.pitch.points.root


def test_ace_mobile_uses_modified_pinyin_as_lyric(tmp_path: pathlib.Path) -> None:
    ace_path = tmp_path / "polyphonic.ace"
    ace_path.write_text(
        json.dumps(
            {
                "song_info": {"bpm": 120},
                "role_info": {"name": "singer", "role_id": 2},
                "notes": [
                    {
                        "start_time": 0.0,
                        "end_time": 0.5,
                        "pitch": 60,
                        "word": "谁",
                        "pinyin": "shei",
                    },
                    {
                        "start_time": 0.5,
                        "end_time": 1.0,
                        "pitch": 62,
                        "word": "水",
                        "pinyin": "shui",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    project = AceMobileConverter.load(
        ace_path,
        {"import_instrumental_track": False},
    )

    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert [(note.lyric, note.pronunciation) for note in track.note_list] == [
        ("shei", None),
        ("水", "shui"),
    ]


def test_ace_mobile_round_trip_new_schema(tmp_path: pathlib.Path) -> None:
    source = Project(
        song_tempo_list=[SongTempo(position=0, bpm=120)],
        time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
        track_list=[
            SingingTrack(
                title="Mobile Singer",
                ai_singer_name="Mobile Singer",
                note_list=[
                    Note(start_pos=0, length=480, key_number=60, lyric="你", pronunciation="ni"),
                    Note(start_pos=480, length=240, key_number=62, lyric="好", pronunciation="hao"),
                ],
            )
        ],
    )
    track = source.track_list[0]
    assert isinstance(track, SingingTrack)
    track.edited_params.pitch.points.root = [
        Point.start_point(),
        Point(1920, -100),
        Point(1920, 6000),
        Point(2160, 6025),
        Point(2400, -100),
        Point.end_point(),
    ]
    ace_path = tmp_path / "roundtrip.ace"

    AceMobileConverter.dump(
        ace_path,
        source,
        {"author": "tester", "role_id": 7, "song_name": "roundtrip"},
    )
    raw = json.loads(ace_path.read_text(encoding="utf-8"))
    parsed_model = AceProject.model_validate(raw)
    assert raw["version"] == 2
    assert raw["song_info"]["name"] == "roundtrip"
    assert raw["tracks"][0]["role_info"] == {"name": "Mobile Singer", "role_id": 7}
    assert len(parsed_model.tracks[0].notes[0].pitch_bends) == 2
    assert [note.pitch for note in parsed_model.tracks[0].notes] == [72, 74]

    restored = AceMobileConverter.load(
        ace_path,
        {"import_instrumental_track": False},
    )
    restored_track = restored.track_list[0]
    assert isinstance(restored_track, SingingTrack)
    assert [
        (note.start_pos, note.length, note.key_number, note.lyric)
        for note in restored_track.note_list
    ] == [
        (0, 480, 60, "你"),
        (480, 240, 62, "好"),
    ]
    assert Point(2160, 6025) in restored_track.edited_params.pitch.points.root


def test_ace_mobile_prefers_precise_user_pitch(tmp_path: pathlib.Path) -> None:
    ace_path = tmp_path / "precise.ace"
    ace_path.write_text(
        json.dumps(
            {
                "version": 2,
                "song_info": {"bpm": 120},
                "tracks": [
                    {
                        "notes": [
                            {
                                "start_time": 1.0,
                                "end_time": 2.0,
                                "pitch": 72,
                                "word": "la",
                                "pitchBends": [
                                    {"time": 1.0, "pitch": 0.0},
                                    {"time": 1.5, "pitch": 0.0},
                                ],
                                "user_pitch": [
                                    {"time": 0.9, "pitch": 0.25},
                                    {"time": 1.5, "pitch": -0.5},
                                ],
                            }
                        ]
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    project = AceMobileConverter.load(ace_path, {"import_instrumental_track": False})

    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert track.note_list[0].key_number == 60
    assert Point(2784, 6025) in track.edited_params.pitch.points.root
    assert Point(3360, 5950) in track.edited_params.pitch.points.root
    assert Point(2880, 7200) not in track.edited_params.pitch.points.root


def test_ace_mobile_version_3_uses_midi_pitch(tmp_path: pathlib.Path) -> None:
    ace_path = tmp_path / "version-3.ace"
    ace_path.write_text(
        json.dumps(
            {
                "version": 3,
                "song_info": {"bpm": 120},
                "tracks": [
                    {
                        "notes": [
                            {
                                "start_time": 0.0,
                                "end_time": 0.5,
                                "pitch": 60,
                                "word": "la",
                            }
                        ]
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    project = AceMobileConverter.load(ace_path, {"import_instrumental_track": False})

    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert track.note_list[0].key_number == 60


def test_ace_mobile_ignores_truncated_trailing_fragment(tmp_path: pathlib.Path) -> None:
    ace_path = tmp_path / "trailing-fragment.ace"
    valid_project = json.dumps(
        {
            "version": 2,
            "song_info": {"bpm": 120},
            "tracks": [
                {
                    "notes": [
                        {
                            "start_time": 0.0,
                            "end_time": 0.5,
                            "pitch": 72,
                            "word": "la",
                        }
                    ]
                }
            ],
        }
    )
    ace_path.write_text(
        valid_project + '9565309618098},{"pitch":0.0,"time":1.0}],"st',
        encoding="utf-8",
    )

    project = AceMobileConverter.load(ace_path, {"import_instrumental_track": False})

    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert track.note_list[0].key_number == 60


def test_acep_pitch_segments_do_not_overlap_at_note_boundaries() -> None:
    project = Project(
        song_tempo_list=[SongTempo(position=0, bpm=120)],
        time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
        track_list=[
            SingingTrack(
                note_list=[
                    Note(start_pos=0, length=480, key_number=60, lyric="a"),
                    Note(start_pos=480, length=480, key_number=62, lyric="b"),
                ]
            )
        ],
    )
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    track.edited_params.pitch.points.root = [
        Point.start_point(),
        Point(1920, 6000),
        Point(2400, 6000),
        Point(2400, -100),
        Point(2400, 6200),
        Point(2880, 6200),
        Point(2880, -100),
        Point.end_point(),
    ]

    ace_project = AceGenerator(AcepOutputOptions()).generate_project(project)
    pattern = ace_project.tracks[0].patterns[0]
    curves = pattern.parameters.pitch_delta.root

    assert [(curve.offset, len(curve.values)) for curve in curves] == [(0, 480), (480, 480)]
    assert all(left.offset + len(left.values) <= right.offset for left, right in pairwise(curves))
    assert all(curve.offset + len(curve.values) <= pattern.dur for curve in curves)


def test_acep_default_output_preserves_breath_adjacent_note_lengths() -> None:
    project = Project(
        song_tempo_list=[SongTempo(position=0, bpm=158)],
        time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
        track_list=[
            SingingTrack(
                note_list=[
                    Note(start_pos=0, length=240, key_number=60, lyric="a"),
                    Note(start_pos=240, length=240, key_number=62, lyric="b", head_tag="V"),
                ]
            )
        ],
    )

    ace_project = AceGenerator(AcepOutputOptions()).generate_project(project)
    notes = ace_project.tracks[0].patterns[0].notes

    assert AcepOutputOptions().breath == 0
    assert [note.dur for note in notes] == [240, 240]
