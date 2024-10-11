import dataclasses
import functools
import operator
from collections.abc import Iterator
from typing import Optional

from sortedcontainers import SortedKeyList

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.exceptions import NoTrackError
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils.translation import gettext_lazy as _

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
    tempos: SortedKeyList[SongTempo] = dataclasses.field(
        default_factory=functools.partial(SortedKeyList, key=operator.attrgetter("position"))
    )

    def parse_project(self, ust_project: UTAUProject) -> Project:
        if not len(ust_project.track):
            raise NoTrackError(_("UST project has no track"))
        tracks = []
        time_signatures = self.parse_time_signatures(ust_project.time_signatures)
        for ust_track in ust_project.track:
            track = SingingTrack()
            for (
                notes,
                mode1_track_pitch_data,
                mode2_track_pitch_data,
            ) in self.parse_notes(ust_project.tempo, ust_track.notes):
                track.note_list.extend(notes)
                if self.options.import_pitch:
                    synchronizer = TimeSynchronizer(list(self.tempos))
                    if ust_project.pitch_mode2:
                        track.edited_params.pitch.points.root.extend(
                            pitch_from_utau_mode2_track(
                                mode2_track_pitch_data, synchronizer, notes
                            ).points.root
                        )
                    else:
                        track.edited_params.pitch.points.root.extend(
                            pitch_from_utau_mode1_track(
                                mode1_track_pitch_data,
                                synchronizer,
                                notes,
                            ).points.root
                        )
            tracks.append(track)
        return Project(
            song_tempo_list=list(self.tempos),
            time_signature_list=time_signatures,
            track_list=tracks,
        )

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
    ) -> Iterator[tuple[list[Note], UtauMode1TrackPitchData, UtauMode2TrackPitchData]]:
        note_list = []
        mode1_track_pitch_data = UtauMode1TrackPitchData()
        mode2_track_pitch_data = UtauMode2TrackPitchData()
        time = 0
        if initial_tempo is not None and not len(self.tempos):
            self.tempos.add(
                SongTempo(
                    position=time,
                    bpm=initial_tempo,
                )
            )
        if not len(self.tempos):
            # TODO: add warning
            self.tempos.add(
                SongTempo(
                    position=time,
                    bpm=DEFAULT_BPM,
                )
            )
        for note in notes:
            if note.tempo is not None:
                self.tempos.add(
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
                    bpm=self.tempos[-1].bpm,
                    start=note.pbs[0] if len(note.pbs) and isinstance(note.pbs[0], float) else None,
                    start_shift=note.pbs[1]
                    if len(note.pbs) > 1 and isinstance(note.pbs[1], float)
                    else None,
                    widths=[x or 0 for x in (note.pbw or [])],
                    shifts=[x or 0 for x in (note.pby or [])],
                    curve_types=note.pbm or [],
                    vibrato_params=note.vbr,
                )
                mode2_track_pitch_data.notes.append(
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
                mode1_track_pitch_data.notes.append(
                    UtauMode1NotePitchData(note.pitch_bend_points)
                    if note.pitch_bend_points
                    else None
                )
            elif note_list:
                yield note_list, mode1_track_pitch_data, mode2_track_pitch_data
                note_list.clear()
                mode1_track_pitch_data.notes.clear()
                mode2_track_pitch_data.notes.clear()
            time += note.length
        if note_list:
            yield note_list, mode1_track_pitch_data, mode2_track_pitch_data
