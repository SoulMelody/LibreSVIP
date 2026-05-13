import io
import pathlib
import zipfile
from itertools import pairwise

import pytest

from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.extension.manager import get_svs_plugin_by_suffix, plugin_manager
from libresvip.model.base import SingingTrack
from libresvip.plugins.mid.midi_parser import cc11_to_db_change
from libresvip.plugins.musicxml.dynamics import DYNAMIC_TO_VELOCITY
from libresvip.plugins.musicxml.musicxml_converter import MusicXMLConverter

musicxml_test_base_path = pathlib.Path(__file__).parent / "files" / "musicxml"
musicxml_v4_path = musicxml_test_base_path / "v4"


def assert_legato(track: SingingTrack) -> None:
    """Assert that all notes in a track are legato, meaning no gaps between notes."""
    for note1, note2 in pairwise(track.note_list):
        assert note1.length == note2.start_pos - note1.start_pos


def test_musicxml_pitches() -> None:
    test_file = musicxml_test_base_path / "01a-Pitches-Pitches.musicxml"

    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    base_tones = [
        43,
        45,
        47,
        48,
        50,
        52,
        53,
        55,
        57,
        59,
        60,
        62,
        64,
        65,
        67,
        69,
        71,
        72,
        74,
        76,
        77,
        79,
        81,
        83,
        84,
        86,
        88,
        89,
        91,
        93,
        95,
        96,
    ]
    tones = (
        base_tones
        + [t + 1 for t in base_tones]
        + [t - 1 for t in base_tones]
        + [64, 65, 67, 69, 71, 72, 74, 76, 74, 70, 73, 73, 73, 73]
    )

    assert_legato(track)
    assert track.note_list[0].start_pos == 0

    assert len(track.note_list) == len(tones)

    for note, expected_tone in zip(track.note_list, tones):
        assert note.length == 480
        assert note.key_number == expected_tone


def test_musicxml_rhythm_durations() -> None:
    test_file = musicxml_test_base_path / "03aa-Rhythm-Durations.musicxml"
    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    base_lengths = [128, 64, 32, 16, 8, 4, 2, 1, 1]
    lengths = (
        [length * 30 for length in base_lengths]
        + [length * 45 for length in base_lengths]
        + [length * 105 for length in base_lengths[2:]]
    )

    assert_legato(track)
    assert track.note_list[0].start_pos == 0
    assert len(track.note_list) == len(lengths)
    for note, expected_length in zip(track.note_list, lengths):
        assert note.key_number == 72
        assert note.length == expected_length


def test_musicxml_rhythm_backup() -> None:
    test_file = musicxml_test_base_path / "03b-Rhythm-Backup.musicxml"

    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    positions = [0, 480, 480, 960]
    tones = [60, 57, 60, 57]

    assert len(track.note_list) == 4

    for note, expected_pos in zip(track.note_list, positions):
        assert note.start_pos == expected_pos, (
            f"Expected position {expected_pos}, got {note.start_pos}"
        )
        assert note.length == 480, (
            f"Note at position {note.start_pos} should have duration 480, got {note.length}"
        )

    for note, expected_tone in zip(track.note_list, tones):
        assert note.key_number == expected_tone, (
            f"Note at position {note.start_pos} should have tone {expected_tone}, got {note.key_number}"
        )


def test_musicxml_chord() -> None:
    test_file = musicxml_test_base_path / "21c-Chords-ThreeNotesDuration.musicxml"

    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    expected_positions = [
        0,
        0,
        0,
        720,
        720,
        960,
        960,
        960,
        1440,
        1440,
        1440,
        1920,
        1920,
        1920,
        2400,
        2400,
        2400,
        2880,
        2880,
        2880,
    ]

    expected_durations = [
        720,
        720,
        720,
        240,
        240,
        480,
        480,
        480,
        480,
        480,
        480,
        480,
        480,
        480,
        480,
        480,
        480,
        960,
        960,
        960,
    ]

    assert len(track.note_list) == len(expected_positions)
    for note, expected_pos, expected_dur in zip(
        track.note_list, expected_positions, expected_durations
    ):
        assert note.start_pos == expected_pos
        assert note.length == expected_dur


def test_musicxml_tie() -> None:
    test_file = musicxml_test_base_path / "33b-Spanners-Tie.musicxml"

    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    assert len(track.note_list) == 1
    note = track.note_list[0]
    assert note.start_pos == 0
    assert note.key_number == 65
    assert note.length == 480 * 8


def test_musicxml_lyrics() -> None:
    test_file = musicxml_test_base_path / "61a-Lyrics.musicxml"
    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    expected_lyrics = [
        "Tralali",
        "+",
        "+",
        "Ja!",
        DEFAULT_PHONEME,
        "Trara!",
        DEFAULT_PHONEME,
        "+",
        DEFAULT_PHONEME,
        "Bah!",
        DEFAULT_PHONEME,
    ]
    assert len(track.note_list) == len(expected_lyrics)
    for note, expected_lyric in zip(track.note_list, expected_lyrics):
        assert note.lyric == expected_lyric


def test_v4_empty_fermata() -> None:
    """An empty <fermata/> element (legal in MusicXML 4.0) used to crash with
    ValidationError. Now it parses, the fermata note is lengthened by the
    'normal' factor (1.5x), and subsequent notes shift by the added duration.
    """
    project = MusicXMLConverter.load(musicxml_v4_path / "v4-empty-fermata.musicxml", {})
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert len(track.note_list) == 5

    extra = round(480 * (1.5 - 1))  # 240

    # Note 0: untouched
    assert track.note_list[0].start_pos == 0
    assert track.note_list[0].length == 480
    # Note 1: fermata stretch
    assert track.note_list[1].start_pos == 480
    assert track.note_list[1].length == 480 + extra
    # Note 2 onwards: shifted by `extra`
    assert track.note_list[2].start_pos == 960 + extra
    assert track.note_list[3].start_pos == 1440 + extra
    assert track.note_list[4].start_pos == 1920 + extra


def test_v4_mid_measure_tempo() -> None:
    """A <direction><sound tempo="60"/></direction> placed two beats into
    measure 2 must produce a SongTempo at the correct mid-measure tick.
    """
    project = MusicXMLConverter.load(musicxml_v4_path / "v4-direction-tempo.musicxml", {})
    assert len(project.song_tempo_list) >= 2
    assert project.song_tempo_list[0].position == 0
    assert project.song_tempo_list[0].bpm == pytest.approx(120.0)
    # measure 1 = 4 quarters at 480 ticks each = 1920; mid-measure 2 after 2 quarters = 960
    assert project.song_tempo_list[1].position == 1920 + 960
    assert project.song_tempo_list[1].bpm == pytest.approx(60.0)


def test_v4_dynamics_curve() -> None:
    """Dynamics markings are converted to volume points on the same scale used
    by the MIDI plugin (cc11_to_db_change of MIDI velocity).
    """
    project = MusicXMLConverter.load(musicxml_v4_path / "v4-dynamics-wedge.musicxml", {})
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    assert track.edited_params is not None
    points = track.edited_params.volume.points.root
    assert len(points) >= 2

    # First point at tick 0 carries the <p> dynamic
    p_value = round(cc11_to_db_change(DYNAMIC_TO_VELOCITY["p"]))
    assert points[0].x == 0
    assert points[0].y == p_value

    # Last point carries the <f> dynamic, at the wedge stop tick
    f_value = round(cc11_to_db_change(DYNAMIC_TO_VELOCITY["f"]))
    assert points[-1].y == f_value
    assert points[-1].y > p_value  # crescendo direction


def test_v4_wedge_crescendo_anchors() -> None:
    """A crescendo wedge must produce a starting anchor at the wedge type=
    "crescendo" tick (carrying the prior dynamic) and an ending anchor at the
    type="stop" tick (carrying the next dynamic).
    """
    project = MusicXMLConverter.load(musicxml_v4_path / "v4-dynamics-wedge.musicxml", {})
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)
    points = track.edited_params.volume.points.root
    ticks = [p.x for p in points]
    # Anchor at tick 960 (after 2 quarter notes, where wedge starts)
    assert 960 in ticks
    # Anchor at tick 1920 (end of measure, where wedge stops + f arrives)
    assert 1920 in ticks
    # Monotonically non-decreasing values across the curve
    for a, b in pairwise(points):
        assert b.y >= a.y


def test_xml_extension_dispatch() -> None:
    """MusicXML is registered once in the plugin list, and all three
    suffixes resolve to the MusicXML converter through suffix lookup.
    """
    plugins = plugin_manager.plugins["svs"]
    assert "musicxml" in plugins, "musicxml not registered"
    converter = plugins["musicxml"]
    assert converter.info.suffixes == ("musicxml", "xml", "mxl"), (
        f"Expected suffixes ('musicxml', 'xml', 'mxl'), got {converter.info.suffixes}"
    )
    for suffix in ("musicxml", "xml", "mxl"):
        resolved = get_svs_plugin_by_suffix(suffix)
        assert resolved is converter, (
            f"suffix '{suffix}' should resolve to the same MusicXML converter"
        )


def test_mxl_extension_compressed(tmp_path: pathlib.Path) -> None:
    """A .mxl (zipped MusicXML) is detected by ZIP magic and parsed identically
    to its .musicxml source.
    """
    source = (musicxml_v4_path / "v4-direction-tempo.musicxml").read_bytes()
    mxl_path = tmp_path / "compressed.mxl"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "META-INF/container.xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                "<container>"
                '<rootfiles><rootfile full-path="score.musicxml" '
                'media-type="application/vnd.recordare.musicxml+xml"/></rootfiles>'
                "</container>"
            ),
        )
        zf.writestr("score.musicxml", source)
    mxl_path.write_bytes(buf.getvalue())

    project = MusicXMLConverter.load(mxl_path, {})
    assert len(project.song_tempo_list) >= 2
    assert project.song_tempo_list[1].position == 1920 + 960


def test_xml_content_sniff_rejects_foreign_xml(tmp_path: pathlib.Path) -> None:
    """A plain <svg/> file fed to the MusicXML loader must produce a clear
    ValueError, not a deep xsdata stack trace.
    """
    foreign = tmp_path / "drawing.xml"
    foreign.write_bytes(b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>')
    with pytest.raises(ValueError, match="not a MusicXML score"):
        MusicXMLConverter.load(foreign, {})
