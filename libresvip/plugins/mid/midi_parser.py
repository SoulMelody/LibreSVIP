import collections
import dataclasses
import math
import operator
from typing import List

import mido
import regex as re
from pydub.utils import ratio_to_db

from libresvip.core.constants import (
    DEFAULT_LYRIC,
    TICKS_IN_BEAT,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Params,
    Point,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .constants import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    EXPRESSION_CONSTANT,
    PITCH_MAX_VALUE,
    VELOCITY_CONSTANT,
    ControlChange,
)
from .note_overlap import has_overlap
from .options import InputOptions, MultiChannelOption


def cc11_to_db_change(value):
    return ratio_to_db((value / 127) ** EXPRESSION_CONSTANT + 1e-6)


def velocity_to_db_change(value):
    return ratio_to_db((value / 127) ** VELOCITY_CONSTANT + 1e-6)


@dataclasses.dataclass
class MidiParser:
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    mido_obj: mido.MidiFile = dataclasses.field(init=False)
    options: InputOptions

    @property
    def tick_rate(self):
        if self.mido_obj is not None:
            return TICKS_IN_BEAT / self.mido_obj.ticks_per_beat
        return 1

    def decode_project(self, mido_obj: mido.MidiFile) -> Project:
        self.mido_obj = mido_obj
        self._convert_delta_to_cumulative(mido_obj.tracks)
        project = Project()
        if len(mido_obj.tracks):
            master_track = mido_obj.tracks[0]
            project.song_tempo_list = self.decode_tempo(master_track)
            self.synchronizer = TimeSynchronizer(
                project.song_tempo_list, _default_tempo=self.options.default_bpm
            )
            project.time_signature_list = self.decode_time_signatures(master_track)
        project.track_list = self.decode_tracks(mido_obj.tracks)
        return project

    @staticmethod
    def _convert_delta_to_cumulative(tracks):
        for track in tracks:
            tick = 0
            for event in track:
                event.time += tick
                tick = event.time

    def decode_time_signatures(self, master_track) -> List[TimeSignature]:
        # no default
        time_signature_changes = [TimeSignature(BarIndex=0, Numerator=4, Denominator=4)]

        # traversing
        if self.options.import_time_signatures:
            prev_ticks = 0
            measure = 0
            for event in master_track:
                if event.type == "time_signature":
                    tick_in_full_note = (
                        self.mido_obj.ticks_per_beat
                        * time_signature_changes[-1].numerator
                    )
                    tick = event.time
                    measure += (tick - prev_ticks) / tick_in_full_note
                    ts_obj = TimeSignature(
                        BarIndex=math.floor(measure),
                        Numerator=event.numerator,
                        Denominator=event.denominator,
                    )
                    time_signature_changes.append(ts_obj)
                    prev_ticks = tick
        return time_signature_changes

    def decode_tempo(self, master_track) -> List[SongTempo]:
        # default bpm
        tempos = [SongTempo(Position=0, BPM=self.options.default_bpm)]

        # traversing
        for event in master_track:
            if event.type == "set_tempo":
                # convert tempo to BPM
                tempo = round(mido.tempo2bpm(event.tempo), 3)
                tick = round(event.time * self.tick_rate)
                if tick == 0:
                    tempos = [SongTempo(Position=0, BPM=tempo)]
                else:
                    last_tempo = tempos[-1].bpm
                    if tempo != last_tempo:
                        tempos.append(SongTempo(Position=tick, BPM=tempo))
        return tempos

    def decode_track(self, track_idx, track) -> SingingTrack:
        last_note_on = collections.defaultdict(list)
        pitchbend_range_changed = collections.defaultdict(list)
        lyrics = collections.defaultdict(lambda: DEFAULT_LYRIC)
        track_name = None
        notes = []
        pitch = ParamCurve()
        expression = ParamCurve()
        pitch_bend_sensitivity = DEFAULT_PITCH_BEND_SENSITIVITY
        volume_base = 0.0
        for event in track:
            # Look for track name events
            if event.type == "track_name":
                # Set the track name for the current track
                track_name = event.name.encode("latin-1").decode(
                    self.options.lyric_encoding, "ignore"
                )
            # Note ons are note on events with velocity > 0
            elif event.type == "note_on" and event.velocity > 0:
                # Store this as the last note-on location
                note_on_index = (event.channel, event.note)
                pitch.points.append(Point(round(event.time * self.tick_rate), 0))
                last_note_on[note_on_index].append(event.time)
            # Note offs can also be note on events with 0 velocity
            elif event.type == "note_off" or (
                event.type == "note_on" and event.velocity == 0
            ):
                # Check that a note-on exists (ignore spurious note-offs)
                key = (event.channel, event.note)
                if key in last_note_on:
                    # Get the start/stop times and velocity of every note
                    # which was turned on with this instrument/drum/pitch.
                    # One note-off may close multiple note-on events from
                    # previous ticks. In case there's a note-off and then
                    # note-on at the same tick we keep the open note from
                    # this tick.
                    end_tick = event.time
                    open_notes = last_note_on[key]

                    notes_to_close = [
                        start_tick
                        for start_tick in open_notes
                        if start_tick != end_tick
                    ]
                    notes_to_keep = [
                        start_tick
                        for start_tick in open_notes
                        if start_tick == end_tick
                    ]

                    for start_tick in notes_to_close:
                        # Create the note event
                        note = Note(
                            KeyNumber=event.note,
                            StartPos=round(start_tick * self.tick_rate),
                            Length=round((end_tick - start_tick) * self.tick_rate),
                        )
                        lyric = lyrics[start_tick]
                        if re.search("[a-zA-Z]", lyric) is not None:
                            note.lyric = DEFAULT_LYRIC
                            note.pronunciation = lyric
                        else:
                            note.lyric = lyric
                        notes.append(note)
                    if len(notes_to_close) > 0 and len(notes_to_keep) > 0:
                        # Note-on on the same tick but we already closed
                        # some previous notes -> it will continue, keep it.
                        last_note_on[key] = notes_to_keep
                    else:
                        # Remove the last note on for this instrument
                        del last_note_on[key]
            # Store pitch bends
            elif event.type == "pitchwheel":
                # Create pitch bend class instance
                pitch.points.append(
                    Point(
                        round(event.time * self.tick_rate),
                        pitch_bend_sensitivity * event.pitch / PITCH_MAX_VALUE,
                    )
                )
            # Store lyrics
            elif event.type == "lyrics":
                if self.options.import_lyrics:
                    lyric = event.text.encode("latin-1").decode(
                        self.options.lyric_encoding
                    )
                    lyrics[event.time] = lyric
            elif event.type == "control_change":
                if (
                    event.control == ControlChange.DATA_ENTRY
                    and len(pitchbend_range_changed[event.time]) >= 2
                ):
                    pitch_bend_sensitivity = event.value
                elif event.control == ControlChange.RPN_MSB and event.value == 0:
                    pitchbend_range_changed[event.time].append(event.value)
                elif event.control == ControlChange.RPN_LSB and event.value == 0:
                    pitchbend_range_changed[event.time].append(event.value)
                elif event.control == ControlChange.EXPRESSION and event.value:
                    expression.points.append(
                        Point(
                            round(event.time * self.tick_rate),
                            round(volume_base + cc11_to_db_change(event.value)),
                        )
                    )
                elif event.control == ControlChange.VOLUME and event.value:
                    volume_base = velocity_to_db_change(event.value)
                else:
                    pass
        pitch.points.__root__.sort(key=operator.attrgetter("x"))
        edited_params = Params(
            Pitch=pitch,
            Volume=expression,
        )
        if has_overlap(notes):
            raise ValueError(f"Notes overlap in track {track_idx}")
        return SingingTrack(
            Title=track_name or f"Track {track_idx + 1}",
            NoteList=notes,
            EditedParams=edited_params,
        )

    def decode_tracks(self, midi_tracks) -> List[Track]:
        tracks = []
        for track_idx, track in enumerate(midi_tracks):
            tracks.append(self.decode_track(track_idx, track))
        return tracks
