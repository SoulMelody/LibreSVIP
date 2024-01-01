import dataclasses
from gettext import gettext as _
from typing import Optional

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.exceptions import NoTrackError
from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature

from .model import UTAUNote, UTAUProject, UTAUTimeSignature
from .options import InputOptions
from .pitch_mode1 import (
    UtauMode1NotePitchData,
    UtauMode1TrackPitchData,
    pitch_from_utau_mode1_track,
)
from .pitch_mode2 import (
    UtauMode2NotePitchData,
    UtauMode2TrackPitchData,
    pitch_from_utau_mode2_track,
)


@dataclasses.dataclass
class USTParser:
    options: InputOptions
    mode1_track_pitch_data: UtauMode1TrackPitchData = dataclasses.field(
        default_factory=UtauMode1TrackPitchData
    )
    mode2_track_pitch_data: UtauMode2TrackPitchData = dataclasses.field(
        default_factory=UtauMode2TrackPitchData
    )

    def parse_project(self, ust_project: UTAUProject) -> Project:
        if len(ust_project.track):
            tracks = []
            time_signatures = self.parse_time_signatures(ust_project.time_signatures)
            for ust_track in ust_project.track:
                tempos, notes = self.parse_notes(ust_project.tempo, ust_track.notes)
                track = SingingTrack(
                    note_list=notes,
                )
                if ust_project.pitch_mode2:
                    track.edited_params.pitch = pitch_from_utau_mode2_track(
                        self.mode2_track_pitch_data, track.note_list, tempos
                    )
                else:
                    track.edited_params.pitch = pitch_from_utau_mode1_track(
                        self.mode1_track_pitch_data,
                        track.note_list,
                    )
                tracks.append(track)
            project = Project(
                song_tempo_list=tempos,
                time_signature_list=time_signatures,
                track_list=tracks,
            )
            return project
        else:
            raise NoTrackError(_("UST project has no track"))

    def parse_time_signatures(
        self, time_signatures: list[UTAUTimeSignature]
    ) -> list[TimeSignature]:
        if not len(time_signatures):
            return [TimeSignature()]
        return [
            TimeSignature(
                numerator=ts.numerator,
                denominator=ts.denominator,
                bar_index=ts.bar_index,
            )
            for ts in time_signatures
        ]

    def parse_notes(
        self, initial_tempo: Optional[float], notes: list[UTAUNote]
    ) -> tuple[list[SongTempo], list[Note]]:
        tempos: list[SongTempo] = []
        note_list = []
        time = 0
        if initial_tempo is not None:
            tempos.append(
                SongTempo(
                    position=time,
                    bpm=initial_tempo,
                )
            )
        if not len(tempos):
            # TODO: add warning
            tempos.append(
                SongTempo(
                    position=time,
                    bpm=DEFAULT_BPM,
                )
            )
        for note in notes:
            if note.tempo is not None:
                tempos.append(
                    SongTempo(
                        position=time,
                        bpm=note.tempo,
                    )
                )
            if note.lyric.upper() != "R":
                note_list.append(
                    Note(
                        lyric=note.lyric,
                        length=note.length,
                        start_pos=time,
                        key_number=note.note_num,
                    )
                )
                mode2_note_pitch_data = UtauMode2NotePitchData(
                    bpm=tempos[-1].bpm,
                    start=note.pbs[0] if len(note.pbs) else None,
                    start_shift=note.pbs[1] if len(note.pbs) > 1 else None,
                    widths=[x or 0 for x in (note.pbw or [])],
                    shifts=[x or 0 for x in (note.pby or [])],
                    curve_types=note.pbm or [],
                    vibrato_params=note.vbr,
                )
                self.mode2_track_pitch_data.notes.append(
                    mode2_note_pitch_data
                    if any(
                        getattr(mode2_note_pitch_data, key) is not None
                        for key in [
                            "start",
                            "start_shift",
                            "widths",
                            "shifts",
                            "curve_types",
                            "vibrato_params",
                        ]
                    )
                    else None
                )
            if note.pitch_bend_points:
                self.mode1_track_pitch_data.notes.append(
                    UtauMode1NotePitchData(note.pitch_bend_points)
                )
            time += note.length
        return tempos, note_list
