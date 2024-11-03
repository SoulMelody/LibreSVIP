import collections
import dataclasses
import itertools
import math
import operator

import mido_fix as mido
import more_itertools

from libresvip.core.constants import (
    DEFAULT_PHONEME,
    DEFAULT_PITCH_BEND_SENSITIVITY,
    PITCH_MAX_VALUE,
    TICKS_IN_BEAT,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import (
    Note,
    ParamCurve,
    Params,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.music_math import ratio_to_db
from libresvip.utils.text import LATIN_ALPHABET
from libresvip.utils.translation import gettext_lazy as _

from .constants import (
    EXPRESSION_CONSTANT,
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
    ticks_per_beat: int = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    selected_channels: list[int] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        if self.options.multi_channel == MultiChannelOption.FIRST:
            self.selected_channels = [0]
        elif self.options.multi_channel == MultiChannelOption.CUSTOM:
            for exp in self.options.channels.split(","):
                if exp:
                    start, sep, end = exp.partition("-")
                    if start.isdigit() and not start.startswith("0"):
                        if not len(end):
                            self.selected_channels.append(int(start) - 1)
                        elif end.isdigit() and not end.startswith("0"):
                            self.selected_channels.extend(range(int(start) - 1, int(end)))

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
            time_signature_list = self.parse_time_signatures(master_track)
        song_tempo_list = self.parse_tempo(mido_obj.tracks)
        self.synchronizer = TimeSynchronizer(song_tempo_list)
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

    def parse_time_signatures(self, master_track: mido.MidiTrack) -> list[TimeSignature]:
        # no default
        time_signature_changes: list[TimeSignature] = []

        # traversing
        if self.options.import_time_signatures:
            prev_ticks = 0
            measure = 0
            for event in master_track:
                if event.type == "time_signature":
                    tick = event.time
                    if not time_signature_changes:
                        tick_in_full_note = 4 * self.ticks_per_beat
                    else:
                        tick_in_full_note = round(
                            time_signature_changes[-1].bar_length(self.ticks_per_beat)
                        )
                    measure += (tick - prev_ticks) / tick_in_full_note
                    ts_obj = TimeSignature(
                        bar_index=math.floor(measure),
                        numerator=event.numerator,
                        denominator=event.denominator,
                    )
                    time_signature_changes.append(ts_obj)
                    prev_ticks = tick
        if not time_signature_changes or time_signature_changes[0].bar_index > 0:
            time_signature_changes.insert(0, TimeSignature(bar_index=0, numerator=4, denominator=4))
        self.first_bar_length = round(time_signature_changes[0].bar_length())
        return time_signature_changes

    def parse_tempo(self, tracks: list[mido.MidiTrack]) -> list[SongTempo]:
        tempos: list[SongTempo] = []

        # traversing
        for track in tracks:
            for event in track:
                if event.type == "set_tempo":
                    # convert tempo to BPM
                    tempo = round(mido.tempo2bpm(event.tempo), 3)
                    tick = round(event.time * self.tick_rate)
                    last_tempo = tempos[-1].bpm if tempos else None
                    if tempo != last_tempo:
                        tempos.append(SongTempo(position=tick, bpm=tempo))
        if not tempos:
            # default bpm
            show_warning(_("No tempo labels found in the imported project."))
            tempos.append(SongTempo(position=0, bpm=self.options.default_bpm))
        else:
            tempos.sort(key=operator.attrgetter("position"))
        return tempos

    def parse_track(self, track_idx: int, track: mido.MidiTrack) -> list[SingingTrack]:
        tracks = []
        event_buckets = more_itertools.bucket(
            (event for event in track if hasattr(event, "channel")),
            key=operator.attrgetter("channel"),
        )
        lyrics: dict[int, str] = collections.defaultdict(lambda: DEFAULT_PHONEME)
        if self.options.import_lyrics:
            for event in track:
                if event.type == "lyrics":
                    lyrics[event.time] = event.text
        for channel in event_buckets:
            if self.selected_channels and channel not in self.selected_channels:
                continue
            last_note_on = collections.defaultdict(list)
            pitchbend_range_changed: dict[int, list[int]] = collections.defaultdict(list)
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
                    rel_pitch_points.append(Point(round(event.time * self.tick_rate), 0))
                    last_note_on[event.note].append(event.time)
                elif event.type == "note_off" or (event.type == "note_on" and event.velocity == 0):
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
                            start_tick for start_tick in open_notes if start_tick != end_tick
                        ]
                        notes_to_keep = [
                            start_tick for start_tick in open_notes if start_tick == end_tick
                        ]

                        for start_tick in notes_to_close:
                            # Create the note event
                            note = Note(
                                key_number=event.note,
                                start_pos=round(start_tick * self.tick_rate),
                                length=round((end_tick - start_tick) * self.tick_rate),
                            )
                            lyric = lyrics[start_tick]
                            if LATIN_ALPHABET.search(lyric) is not None:
                                note.pronunciation = lyric
                            note.lyric = lyric
                            notes.append(note)
                        if notes_to_close and notes_to_keep:
                            # Note-on on the same tick but we already closed
                            # some previous notes -> it will continue, keep it.
                            last_note_on[key] = notes_to_keep
                        else:
                            # Remove the last note on for this instrument
                            del last_note_on[key]
                elif event.type == "pitchwheel" and self.options.import_pitch:
                    # Create pitch bend class instance
                    rel_pitch_points.append(
                        Point(
                            round(event.time * self.tick_rate),
                            round(
                                pitch_bend_sensitivity
                                * event.pitch
                                / (PITCH_MAX_VALUE if event.pitch > 0 else (PITCH_MAX_VALUE + 1))
                            ),
                        )
                    )
                elif event.type == "control_change":
                    if self.options.import_pitch:
                        if (
                            event.is_cc(ControlChange.DATA_ENTRY)
                            and len(pitchbend_range_changed[event.time]) >= 2
                        ):
                            pitch_bend_sensitivity = event.value
                        elif (
                            event.is_cc(ControlChange.RPN_MSB)
                            and event.value == 0
                            or event.is_cc(ControlChange.RPN_LSB)
                            and event.value == 0
                        ):
                            pitchbend_range_changed[event.time].append(event.value)
                    if self.options.import_volume:
                        if event.is_cc(ControlChange.EXPRESSION) and event.value:
                            expression.points.append(
                                Point(
                                    round(event.time * self.tick_rate),
                                    round(volume_base + cc11_to_db_change(event.value)),
                                )
                            )
                        elif event.is_cc(ControlChange.VOLUME) and event.value:
                            volume_base = velocity_to_db_change(event.value)
            if has_overlap(notes):
                msg = _("Overlapping notes in track {}").format(track_idx)
                show_warning(msg)
            edited_params = Params(volume=expression)
            if self.options.import_pitch:
                pitch_simulator = PitchSimulator(
                    synchronizer=self.synchronizer,
                    portamento=PortamentoPitch.no_portamento(),
                    note_list=notes,
                )
                rel_pitch_points.sort(key=operator.attrgetter("x"))
                edited_params.pitch = RelativePitchCurve(self.first_bar_length).to_absolute(
                    rel_pitch_points, pitch_simulator
                )
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
        return [
            *itertools.chain.from_iterable(
                (self.parse_track(track_idx, track) for track_idx, track in enumerate(midi_tracks)),
            )
        ]
