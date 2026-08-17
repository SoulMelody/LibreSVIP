from libresvip.plugins.aisp.aisingers_parser import AiSingersParser
from libresvip.plugins.aisp.model import AISNote
from libresvip.plugins.aisp.options import InputOptions


def test_parse_note_without_pitch_points() -> None:
    # AISNote.pit defaults to an empty list, so a note without pitch data used
    # to divide note.length by len(pit) == 0 and raise ZeroDivisionError.
    parser = AiSingersParser(options=InputOptions(import_pitch=True))
    parser.first_bar_length = 1920

    note = AISNote(s=0, l=480, m=60, ly="a", py="a", pit=[])
    notes, pitch_points = parser.parse_notes([note], 0)

    assert len(notes) == 1
    assert pitch_points == []


def test_parse_note_with_pitch_points() -> None:
    parser = AiSingersParser(options=InputOptions(import_pitch=True))
    parser.first_bar_length = 1920

    note = AISNote(s=0, l=480, m=60, ly="a", py="a", pit=[1.0, 2.0, 3.0])
    notes, pitch_points = parser.parse_notes([note], 0)

    assert len(notes) == 1
    # start marker, one point per pitch value, and an end marker
    assert len(pitch_points) == 5
