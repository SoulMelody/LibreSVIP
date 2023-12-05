import collections
import dataclasses
import math
import operator
import re
from gettext import gettext as _

import mido_fix as mido
import more_itertools

from libresvip.core.constants import DEFAULT_PHONEME, TICKS_IN_BEAT
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
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils import ratio_to_db

from .constants import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    EXPRESSION_CONSTANT,
    PITCH_MAX_VALUE,
    VELOCITY_CONSTANT,
    ControlChange,
)
from .note_overlap import has_overlap
from .options import InputOptions, MultiChannelOption


def cc11_to_db_change(value: float) -> float:
    return ratio_to_db((value / 127) ** EXPRESSION_CONSTANT + 1e-6)


def velocity_to_db_change(value: float) -> float:
    return ratio_to_db((value / 127) ** VELOCITY_CONSTANT + 1e-6)


@dataclasses.dataclass
class MidiParser:
    options: InputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    ticks_per_beat: int = dataclasses.field(init=False)
    selected_channels: list[int] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if self.options.multi_channel == MultiChannelOption.FIRST:
            self.selected_channels = [0]
        elif self.options.multi_channel == MultiChannelOption.CUSTOM:
            for exp in self.options.channels.split(","):
                if exp:
                    start, sep, end = exp.partition("-")
                    if start.isdigit():
                        if not len(end):
                            self.selected_channels.append(int(start))
                        elif end.isdigit():
                            self.selected_channels.extend(
                                range(int(start), int(end) + 1)
                            )

    @property
    def tick_rate(self) -> float:
        if self.ticks_per_beat is not None:
            return TICKS_IN_BEAT / self.ticks_per_beat
        return 1

    def parse_project(self, mido_obj: mido.MidiFile) -> Project:
        self.ticks_per_beat = mido_obj.ticks_per_beat
        self._convert_delta_to_cumulative(mido_obj.tracks)
        if len(mido_obj.tracks):
            master_track = mido_obj.tracks[0]
            song_tempo_list = self.parse_tempo(master_track)
            self.synchronizer = TimeSynchronizer(
                song_tempo_list, _default_tempo=self.options.default_bpm
            )
            time_signature_list = self.parse_time_signatures(master_track)
        return Project(
            song_tempo_list=song_tempo_list,
            time_signature_list=time_signature_list,
            track_list=self.parse_tracks(mido_obj.tracks),
        )

    @staticmethod
    def _convert_delta_to_cumulative(tracks: list[mido.MidiTrack]) -> None:
        for track in tracks:
            tick = 0
            for event in track:
                event.time += tick
                tick = event.time

    def parse_time_signatures(
        self, master_track: mido.MidiTrack
    ) -> list[TimeSignature]:
        # no default
        time_signature_changes = [
            TimeSignature(bar_index=0, numerator=4, denominator=4)
        ]

        # traversing
        if self.options.import_time_signatures:
            prev_ticks = 0
            measure = 0
            for event in master_track:
                if event.type == "time_signature":
                    tick_in_full_note = time_signature_changes[-1].bar_length(
                        self.ticks_per_beat
                    )
                    tick = event.time
                    measure += (tick - prev_ticks) / tick_in_full_note
                    ts_obj = TimeSignature(
                        bar_index=math.floor(measure),
                        numerator=event.numerator,
                        denominator=event.denominator,
                    )
                    time_signature_changes.append(ts_obj)
                    prev_ticks = tick
        return time_signature_changes

    def parse_tempo(self, master_track: mido.MidiTrack) -> list[SongTempo]:
        # default bpm
        tempos = [SongTempo(position=0, bpm=self.options.default_bpm)]

        # traversing
        for event in master_track:
            if event.type == "set_tempo":
                # convert tempo to BPM
                tempo = round(mido.tempo2bpm(event.tempo), 3)
                tick = round(event.time * self.tick_rate)
                if tick == 0:
                    tempos = [SongTempo(position=0, bpm=tempo)]
                else:
                    last_tempo = tempos[-1].bpm
                    if tempo != last_tempo:
                        tempos.append(SongTempo(position=tick, bpm=tempo))
        return tempos

    def parse_track(self, track_idx: int, track: mido.MidiTrack) -> list[SingingTrack]:
        tracks = []
        event_buckets = more_itertools.bucket(
            (event for event in track if hasattr(event, "channel")),
            key=operator.attrgetter("channel"),
        )
        for channel in event_buckets:
            if self.selected_channels and channel not in self.selected_channels:
                continue
            last_note_on = collections.defaultdict(list)
            pitchbend_range_changed = collections.defaultdict(list)
            lyrics = collections.defaultdict(lambda: DEFAULT_PHONEME)
            track_name = None
            notes = []
            rel_pitch_points = []
            expression = ParamCurve()
            pitch_bend_sensitivity = DEFAULT_PITCH_BEND_SENSITIVITY
            volume_base = 0.0
            for event in event_buckets[channel]:
                # Look for track name events
                if event.type == "track_name":
                    # Set the track name for the current track
                    track_name = event.name
                elif event.type == "note_on" and event.velocity > 0:
                    # Store this as the last note-on location
                    rel_pitch_points.append(
                        Point(round(event.time * self.tick_rate), 0)
                    )
                    last_note_on[event.note].append(event.time)
                elif event.type == "note_off" or (
                    event.type == "note_on" and event.velocity == 0
                ):
                    # Check that a note-on exists (ignore spurious note-offs)
                    key = event.note
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
                                key_number=event.note,
                                start_pos=round(start_tick * self.tick_rate),
                                length=round((end_tick - start_tick) * self.tick_rate),
                            )
                            lyric = lyrics[start_tick]
                            if re.search("[a-zA-Z]", lyric) is not None:
                                note.lyric = DEFAULT_PHONEME
                                note.pronunciation = lyric
                            else:
                                note.lyric = lyric
                            notes.append(note)
                        if notes_to_close and notes_to_keep:
                            # Note-on on the same tick but we already closed
                            # some previous notes -> it will continue, keep it.
                            last_note_on[key] = notes_to_keep
                        else:
                            # Remove the last note on for this instrument
                            del last_note_on[key]
                elif event.type == "pitchwheel":
                    # Create pitch bend class instance
                    rel_pitch_points.append(
                        Point(
                            round(event.time * self.tick_rate),
                            round(
                                pitch_bend_sensitivity * event.pitch / PITCH_MAX_VALUE
                            ),
                        )
                    )
                elif event.type == "lyrics":
                    if self.options.import_lyrics:
                        lyric = event.text
                        lyrics[event.time] = lyric
                elif event.type == "control_change":
                    if (
                        event.is_cc(ControlChange.DATA_ENTRY)
                        and len(pitchbend_range_changed[event.time]) >= 2
                    ):
                        pitch_bend_sensitivity = event.value
                    elif event.is_cc(ControlChange.RPN_MSB) and event.value == 0:
                        pitchbend_range_changed[event.time].append(event.value)
                    elif event.is_cc(ControlChange.RPN_LSB) and event.value == 0:
                        pitchbend_range_changed[event.time].append(event.value)
                    elif event.is_cc(ControlChange.EXPRESSION) and event.value:
                        expression.points.append(
                            Point(
                                round(event.time * self.tick_rate),
                                round(volume_base + cc11_to_db_change(event.value)),
                            )
                        )
                    elif event.is_cc(ControlChange.VOLUME) and event.value:
                        volume_base = velocity_to_db_change(event.value)
            rel_pitch_points.sort(key=operator.attrgetter("x"))
            pitch = RelativePitchCurve().to_absolute(rel_pitch_points, notes)
            edited_params = Params(
                pitch=pitch,
                volume=expression,
            )
            if has_overlap(notes):
                msg = _("Overlapping notes in track {}").format(track_idx)
                raise ValueError(msg)
            if len(notes):
                tracks.append(
                    SingingTrack(
                        title=track_name or f"Track {track_idx + 1} ({channel})",
                        note_list=notes,
                        edited_params=edited_params,
                    )
                )
        return tracks

    def parse_tracks(self, midi_tracks: list[mido.MidiTrack]) -> list[Track]:
        return sum(
            (
                self.parse_track(track_idx, track)
                for track_idx, track in enumerate(midi_tracks)
            ),
            [],
        )
