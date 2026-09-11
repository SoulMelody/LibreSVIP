from libresvip.middlewares.remove_lyric_symbols.remove_lyric_symbols import (
    RemoveLyricSymbolsMiddleware,
    remove_numbers_and_punctuation,
)
from libresvip.model.base import InstrumentalTrack, Note, Project, SingingTrack


def test_remove_numbers_and_punctuation_handles_unicode_characters() -> None:
    assert remove_numbers_and_punctuation("Verse 1\u0662\uff13,\uff0c!。") == "Verse "


def test_remove_numbers_and_punctuation_removes_hyphens_and_dashes() -> None:
    assert remove_numbers_and_punctuation("co-operate\u2014now") == "cooperatenow"


def test_remove_numbers_and_punctuation_preserves_structural_lyrics() -> None:
    for lyric in ("-", "+", "+~", "+*"):
        assert remove_numbers_and_punctuation(lyric) == lyric


def test_middleware_updates_singing_lyrics_without_removing_notes() -> None:
    cleaned_note = Note(start_pos=120, length=480, lyric="123!?", pronunciation="s a")
    structural_note = Note(start_pos=600, length=480, lyric="+~")
    project = Project(
        track_list=[
            SingingTrack(note_list=[cleaned_note, structural_note]),
            InstrumentalTrack(audio_file_path="backing.wav"),
        ]
    )

    result = RemoveLyricSymbolsMiddleware.process(project, {})

    assert result is project
    assert cleaned_note.lyric == ""
    assert cleaned_note.start_pos == 120
    assert cleaned_note.length == 480
    assert cleaned_note.pronunciation == "s a"
    assert structural_note.lyric == "+~"
    assert len(result.track_list) == 2
