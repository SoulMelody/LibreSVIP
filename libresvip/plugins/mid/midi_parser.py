import collections
import dataclasses
import itertools
import math
import operator
from typing import Annotated

import more_itertools
from construct import Container

from libresvip.core.constants import (
    DEFAULT_PHONEME,
    TICKS_IN_BEAT,
)
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.core.tick_counter import find_bar_index
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
)
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.binary.midi import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    PITCH_MAX_VALUE,
    MIDIFile,
    MIDITrack,
    tempo2bpm,
)
from libresvip.utils.music_math import ratio_to_db
from libresvip.utils.text import LATIN_ALPHABET
from libresvip.utils.translation import gettext_lazy as _

from .constants import (
    EXPRESSION_CONSTANT,
    VELOCITY_CONSTANT,
    ControlChange,
)
from .note_overlap import overlapped_pos
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
    time_signatures: list[TimeSignature] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        if self.options.multi_channel.value == MultiChannelOption.FIRST.value:
            self.selected_channels = [0]
        elif self.options.multi_channel.value == MultiChannelOption.CUSTOM.value:
            for exp in self.options.channels.split(","):
                if exp:
                    start, _sep, end = exp.partition("-")
                    if start.isdigit() and not start.startswith("0"):
                        if not len(end):
                            self.selected_channels.append(int(start) - 1)
                        elif end.isdigit() and not end.startswith("0"):
                            self.selected_channels.extend(range(int(start) - 1, int(end)))

    @property
    def tick_rate(self) -> float:
        return TICKS_IN_BEAT / self.ticks_per_beat

    def parse_project(self, mido_obj: Annotated[Container, MIDIFile]) -> Project:
        if mido_obj.ticks_per_beat < 0:
            msg = _("MIDI file with SMPTE time division is not supported.")
            raise NotImplementedError(msg)
        self.ticks_per_beat = mido_obj.ticks_per_beat
        self._convert_delta_to_cumulative(mido_obj.tracks)
        if len(mido_obj.tracks):
            master_track = mido_obj.tracks[0]
            self.time_signatures.extend(self.parse_time_signatures(master_track))
        song_tempo_list = self.parse_tempo(mido_obj.tracks)
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return Project(
            song_tempo_list=song_tempo_list,
            time_signature_list=self.time_signatures,
            track_list=self.parse_tracks(mido_obj.tracks),
        )

    @staticmethod
    def _convert_delta_to_cumulative(tracks: list[Annotated[Container, MIDITrack]]) -> None:
        for track in tracks:
            tick = 0
            for event in track:
                event.time += tick
                tick = event.time

    def parse_time_signatures(
        self, master_track: Annotated[Container, MIDITrack]
    ) -> list[TimeSignature]:
        # no default
        time_signature_changes: list[TimeSignature] = []

        # traversing
        if self.options.import_time_signatures:
            prev_ticks = 0
            measure = 0
            for event in master_track:
                if event.detail.type == "meta" and event.detail.data.type == "time_signature":
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
                        numerator=event.detail.data.numerator,
                        denominator=event.detail.data.denominator,
                    )
                    time_signature_changes.append(ts_obj)
                    prev_ticks = tick
        if not time_signature_changes or time_signature_changes[0].bar_index > 0:
            time_signature_changes.insert(0, TimeSignature(bar_index=0, numerator=4, denominator=4))
        self.first_bar_length = round(time_signature_changes[0].bar_length())
        return time_signature_changes

    def parse_tempo(self, tracks: list[Annotated[Container, MIDITrack]]) -> list[SongTempo]:
        tempos: list[SongTempo] = []

        # traversing
        for track in tracks:
            for event in track:
                if event.detail.type == "meta" and event.detail.data.type == "set_tempo":
                    # convert tempo to BPM
                    tempo = round(tempo2bpm(event.detail.data.tempo), 3)
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

    def parse_track(
        self, track_idx: int, track: Annotated[Container, MIDITrack]
    ) -> list[SingingTrack]:
        tracks = []
        event_buckets = more_itertools.bucket(
            (event for event in track if event.detail.type == "channel"),
            key=lambda event: event.detail.channel,
        )
        lyrics: dict[int, str] = collections.defaultdict(lambda: DEFAULT_PHONEME)
        if self.options.import_lyrics:
            for event in track:
                if event.detail.type == "meta" and event.detail.data.type == "lyrics":
                    lyrics[event.time] = event.detail.data.text.decode(
                        self.options.lyric_encoding, "ignore"
                    )
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
                if event.detail.data.type == "track_name":
                    # Set the track name for the current track
                    track_name = event.name.decode(self.options.track_name_encoding, "ignore")
                elif event.detail.data.type == "note_on" and event.detail.data.velocity > 0:
                    # Store this as the last note-on location
                    rel_pitch_points.append(Point(round(event.time * self.tick_rate), 0))
                    last_note_on[event.detail.data.note].append(event.time)
                elif event.detail.data.type == "note_off" or (
                    event.detail.data.type == "note_on" and event.detail.data.velocity == 0
                ):
                    # Check that a note-on exists (ignore spurious note-offs)
                    key = event.detail.data.note
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
                                key_number=key,
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
                elif event.detail.data.type == "pitchwheel" and self.options.import_pitch:
                    # Create pitch bend class instance
                    rel_pitch_points.append(
                        Point(
                            round(event.time * self.tick_rate),
                            round(
                                pitch_bend_sensitivity
                                * event.detail.data.pitch
                                / (
                                    PITCH_MAX_VALUE
                                    if event.detail.data.pitch > 0
                                    else (PITCH_MAX_VALUE + 1)
                                )
                            ),
                        )
                    )
                elif event.detail.data.type == "control_change":
                    if self.options.import_pitch:
                        if (
                            event.detail.data.control == ControlChange.DATA_ENTRY
                            and len(pitchbend_range_changed[event.time]) >= 2
                        ):
                            pitch_bend_sensitivity = event.value
                        elif (
                            event.detail.data.control == ControlChange.RPN_MSB
                            and event.detail.data.value == 0
                        ) or (
                            event.detail.data.control == ControlChange.RPN_LSB
                            and event.detail.data.value == 0
                        ):
                            pitchbend_range_changed[event.time].append(event.detail.data.value)
                    if self.options.import_volume:
                        if (
                            event.detail.data.control == ControlChange.EXPRESSION
                            and event.detail.data.value
                        ):
                            expression.points.append(
                                Point(
                                    round(event.time * self.tick_rate),
                                    round(volume_base + cc11_to_db_change(event.detail.data.value)),
                                )
                            )
                        elif (
                            event.detail.data.control == ControlChange.VOLUME
                            and event.detail.data.value
                        ):
                            volume_base = velocity_to_db_change(event.detail.data.value)
            if (pos := overlapped_pos(notes)) is not None:
                msg = _("Notes overlapped near bar {}").format(
                    find_bar_index(self.time_signatures, pos)
                )
                raise NotesOverlappedError(msg)
            edited_params = Params(volume=expression)
            if self.options.import_pitch:
                pitch_simulator = PitchSimulator(
                    synchronizer=self.synchronizer,
                    portamento=PortamentoPitch.no_portamento(),
                    note_list=notes,
                    time_signature_list=self.time_signatures,
                )
                rel_pitch_points.sort(key=operator.attrgetter("x"))
                edited_params.pitch = RelativePitchCurve(self.first_bar_length).to_absolute(
                    rel_pitch_points, pitch_simulator
                )
            if notes:
                tracks.append(
                    SingingTrack(
                        title=track_name or f"Track {track_idx + 1} ({channel})",
                        note_list=notes,
                        edited_params=edited_params,
                    )
                )
        return tracks

    def parse_tracks(
        self, midi_tracks: list[Annotated[Container, MIDITrack]]
    ) -> list[SingingTrack]:
        return [
            *itertools.chain.from_iterable(
                (self.parse_track(track_idx, track) for track_idx, track in enumerate(midi_tracks)),
            )
        ]
