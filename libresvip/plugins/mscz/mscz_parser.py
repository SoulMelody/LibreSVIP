import ms3
import pandas
from py_linq.py_linq import Enumerable

from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
)

RESOLUTION = 480


class MsczParser:
    def parse_note(
        self, msNote, lyricsDict: dict[int, str], slursList: list[int], tiesDict: dict[int, Note]
    ) -> Note:
        if msNote.chord_id in slursList:
            lyric = "-"
        elif msNote.chord_id in lyricsDict:
            lyric = lyricsDict[msNote.chord_id]
        else:
            lyric = "a"

        # msNote.tied: 1:start, 0:middle, -1:end
        if pandas.notna(msNote.tied) and (msNote.tied == 0 or msNote.tied == -1):
            tiesDict[msNote.midi].length = (
                round((msNote.quarterbeats + msNote.duration_qb) * RESOLUTION)
                - tiesDict[msNote.midi].start_pos
            )
            if msNote.tied == -1:
                tiesDict.pop(msNote.midi)
            return None

        result = Note(
            StartPos=round(msNote.quarterbeats * RESOLUTION),
            Length=round((msNote.quarterbeats + msNote.duration_qb) * RESOLUTION)
            - round(msNote.quarterbeats * RESOLUTION),
            KeyNumber=msNote.midi,
            Lyric=lyric,
        )
        if pandas.notna(msNote.tied) and msNote.tied == 1:
            tiesDict[msNote.midi] = result
        return result

    def parse_track(
        self,
        msNoteGroup,
        lyricsDict: dict[int, str],
        slursList: list[int],
        tiesDict: dict[int, Note],
    ) -> SingingTrack:
        return SingingTrack(
            NoteList=Enumerable(msNoteGroup)
            .select(lambda n: self.parse_note(n, lyricsDict, slursList, tiesDict))
            .where(lambda n: n != None)
            .to_list()
        )

    def parse_project(self, score: ms3.Score) -> Project:
        if "lyrics_1" in score.mscx.chords().columns:
            lyrics = score.mscx.chords().lyrics_1
        else:
            lyrics = []
        lyricsDict = {i: lyric for (i, lyric) in enumerate(lyrics) if type(lyric) == str}

        if (
            "Chord/Spanner:type" in score.mscx.events().columns
            and "Chord/Spanner/Slur/eid" in score.mscx.events().columns
        ):
            slursList = (
                Enumerable(score.mscx.events().iterrows())
                .select(lambda n: n[1])
                .where(lambda e: e["Chord/Spanner:type"] == "Slur")
                .where(lambda e: type(e["Chord/Spanner/Slur/eid"]) != str)
                .select(lambda e: e.chord_id)
                .to_list()
            )
        else:
            slursList = []

        tiesDict: dict[
            int, Note
        ] = {}  # {tone, the previous note of this tone within an incomplete tie}

        trackList = (
            Enumerable(score.mscx.notes().iterrows())
            .select(lambda n: n[1])
            .group_by(key_names=["staff"], key=lambda n: n["staff"])
            .select(lambda tr: self.parse_track(tr, lyricsDict, slursList, tiesDict))
            .to_list()
        )

        return Project(TrackList=trackList)
