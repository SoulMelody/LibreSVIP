import pathlib
from itertools import pairwise

import pytest

from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.model.base import SingingTrack
from libresvip.plugins.musicxml.musicxml_converter import MusicXMLConverter

musicxml_test_base_path = pathlib.Path(__file__).parent / "files" / "musicxml"

def assert_legato(track: SingingTrack) -> None:
    """Assert that all notes in a track are legato, meaning no gaps between notes."""
    for note1, note2 in pairwise(track.note_list):
        assert note1.length == note2.start_pos - note1.start_pos


def test_musicxml_pitches():
    test_file = musicxml_test_base_path / "01a-Pitches-Pitches.musicxml"

    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    base_tones = [
        43, 45, 47, 48,
        50, 52, 53, 55,
        57, 59, 60, 62,
        64, 65, 67, 69,
        71, 72, 74, 76,
        77, 79, 81, 83,
        84, 86, 88, 89,
        91, 93, 95, 96,
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

def test_musicxml_rhythm_durations():
    test_file = musicxml_test_base_path / "03aa-Rhythm-Durations.musicxml"
    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    base_lengths = [128, 64, 32, 16, 8, 4, 2, 1, 1]
    lengths = (
        [l*30 for l in base_lengths] 
        + [l*45 for l in base_lengths] 
        + [l*105 for l in base_lengths[2:]]
    )

    assert_legato(track)
    assert track.note_list[0].start_pos == 0
    assert len(track.note_list) == len(lengths)
    for note, expected_length in zip(track.note_list, lengths):
        assert note.key_number == 72
        assert note.length == expected_length

def test_musicxml_rhythm_backup():
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

def test_musicxml_chord():
    test_file = musicxml_test_base_path / "21c-Chords-ThreeNotesDuration.musicxml"

    project = MusicXMLConverter.load(test_file, {})

    assert len(project.track_list) == 1
    track = project.track_list[0]
    assert isinstance(track, SingingTrack)

    expected_positions = [
        0, 0, 0,
        720, 720,
        960, 960, 960,
        1440, 1440, 1440,
        1920, 1920, 1920,
        2400, 2400, 2400,
        2880, 2880, 2880,
    ]

    expected_durations = [
        720, 720, 720,
        240, 240,
        480, 480, 480,
        480, 480, 480,
        480, 480, 480,
        480, 480, 480,
        960, 960, 960,
    ]

    assert len(track.note_list) == len(expected_positions)
    for note, expected_pos, expected_dur in zip(
        track.note_list, expected_positions, expected_durations
    ):
        assert note.start_pos == expected_pos
        assert note.length == expected_dur

def test_musicxml_tie():
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

def test_musicxml_lyrics():
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