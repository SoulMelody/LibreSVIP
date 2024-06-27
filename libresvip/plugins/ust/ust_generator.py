import dataclasses

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.exceptions import NoTrackError
from libresvip.model.base import Project, SingingTrack, SongTempo
from libresvip.utils.translation import gettext_lazy as _

from .model import UTAUNote, UTAUProject, UTAUTrack
from .options import OutputOptions
from .pitch_mode1 import pitch_to_utau_mode1_track
from .pitch_mode2 import bpm_for_note, pitch_to_utau_mode2_track


@dataclasses.dataclass
class USTGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> UTAUProject:
        if not project.song_tempo_list:
            project.song_tempo_list.append(SongTempo(bpm=DEFAULT_BPM))
        tempo = project.song_tempo_list[0].bpm
        if self.options.version < 2.0:
            if self.options.track_index < 0:
                first_singing_track = next(
                    (track for track in project.track_list if isinstance(track, SingingTrack)),
                    None,
                )
            else:
                first_singing_track = project.track_list[self.options.track_index]
            if first_singing_track is None or not isinstance(first_singing_track, SingingTrack):
                msg = _("No singing track found")
                raise NoTrackError(msg)
            ust_tracks = [self.generate_track(first_singing_track, project.song_tempo_list)]
        else:
            singing_tracks = [
                track for track in project.track_list if isinstance(track, SingingTrack)
            ]
            if not len(singing_tracks):
                msg = _("No singing track found")
                raise NoTrackError(msg)
            ust_tracks = [
                self.generate_track(track, project.song_tempo_list) for track in singing_tracks
            ]
        return UTAUProject(
            charset=self.options.encoding,
            ust_version=self.options.version,
            tempo=tempo,
            track=ust_tracks,
            pitch_mode2=True,
        )

    def generate_track(self, track: SingingTrack, tempo_list: list[SongTempo]) -> UTAUTrack:
        mode1_track_pitch_data = pitch_to_utau_mode1_track(
            track.edited_params.pitch, track.note_list
        )
        mode2_track_pitch_data = pitch_to_utau_mode2_track(
            track.edited_params.pitch, track.note_list, tempo_list
        )
        utau_notes = []
        prev_bpm = tempo_list[0].bpm
        prev_end_pos = None
        note_index = 0
        for note, mode1_pitch, mode2_pitch in zip(
            track.note_list,
            mode1_track_pitch_data.notes,
            mode2_track_pitch_data.notes,
        ):
            if rest_length := note.start_pos - (prev_end_pos if prev_end_pos is not None else 0):
                rest_note = UTAUNote(
                    note_type=str(note_index).zfill(4),
                    lyric="R",
                    length=rest_length,
                    note_num=60,
                )
                utau_notes.append(rest_note)
                note_index += 1
            cur_bpm = bpm_for_note(tempo_list, note)
            utau_note = UTAUNote(
                note_type=str(note_index).zfill(4),
                lyric=note.lyric,
                length=note.length,
                note_num=note.key_number,
                pitch_bend_points=mode1_pitch.pitch_points if mode1_pitch is not None else [],
                pitchbend_type="5",
                pitchbend_start=0,
            )
            if mode2_pitch:
                if mode2_pitch.start is not None:
                    utau_note.pbs = [mode2_pitch.start]
                if mode2_pitch.widths:
                    utau_note.pbw = [1, *mode2_pitch.widths]
                if mode2_pitch.start_shift is not None:
                    utau_note.pby = [mode2_pitch.start_shift]
                if mode2_pitch.shifts:
                    utau_note.pby += mode2_pitch.shifts
                if mode2_pitch.curve_types:
                    utau_note.pbm = mode2_pitch.curve_types
                if mode2_pitch.vibrato_params:
                    utau_note.vbr = mode2_pitch.vibrato_params
            if cur_bpm != prev_bpm:
                utau_note.tempo = cur_bpm
                prev_bpm = cur_bpm
            utau_notes.append(utau_note)
            prev_end_pos = note.end_pos
            note_index += 1
        return UTAUTrack(notes=utau_notes)
