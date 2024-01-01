import dataclasses

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.exceptions import NoTrackError
from libresvip.model.base import Project, SingingTrack, SongTempo

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
                    (
                        track
                        for track in project.track_list
                        if isinstance(track, SingingTrack)
                    ),
                    None,
                )
            else:
                first_singing_track = project.track_list[self.options.track_index]
            if first_singing_track is None or not isinstance(
                first_singing_track, SingingTrack
            ):
                msg = "No singing track found"
                raise NoTrackError(msg)
            ust_tracks = [
                self.generate_track(first_singing_track, project.song_tempo_list)
            ]
        else:
            singing_tracks = [
                track for track in project.track_list if isinstance(track, SingingTrack)
            ]
            if not len(singing_tracks):
                msg = "No singing track found"
                raise NoTrackError(msg)
            ust_tracks = [
                self.generate_track(track, project.song_tempo_list)
                for track in singing_tracks
            ]
        return UTAUProject(
            charset=self.options.encoding,
            ust_version=self.options.version,
            tempo=tempo,
            track=ust_tracks,
            pitch_mode2=True,
        )

    def generate_track(
        self, track: SingingTrack, tempo_list: list[SongTempo]
    ) -> UTAUTrack:
        mode1_track_pitch_data = pitch_to_utau_mode1_track(
            track.edited_params.pitch, track.note_list
        )
        mode2_track_pitch_data = pitch_to_utau_mode2_track(
            track.edited_params.pitch, track.note_list, tempo_list
        )
        utau_notes = []
        prev_bpm = tempo_list[0].bpm
        for i, (note, mode1_pitch, mode2_pitch) in enumerate(
            zip(
                track.note_list,
                mode1_track_pitch_data.notes,
                mode2_track_pitch_data.notes,
            )
        ):
            cur_bpm = bpm_for_note(tempo_list, note)
            utau_note = UTAUNote(
                note_type=str(i).zfill(4),
                lyric=note.lyric,
                length=note.length,
                note_num=note.key_number,
                pitch_bend_points=mode1_pitch.pitch_points,
                pitchbend_type="5",
                pitchbend_start=0,
            )
            if mode2_pitch:
                utau_note.pbs = [mode2_pitch.start]
                if mode2_pitch.widths:
                    utau_note.pbw = [1] + mode2_pitch.widths
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
        return UTAUTrack(
            notes=utau_notes,
        )
