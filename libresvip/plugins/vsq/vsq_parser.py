import configparser
import dataclasses
import math
import re
from typing import Optional

import mido_fix as mido

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .options import BreathOption, InputOptions
from .vocaloid_pitch import (
    ControllerEvent,
    VocaloidPartPitchData,
    pitch_from_vocaloid_parts,
)

BREATH_PATTERN = re.compile("br[1-5]")


@dataclasses.dataclass
class VsqParser:
    options: InputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    ticks_per_beat: int = dataclasses.field(init=False)

    @property
    def tick_rate(self) -> float:
        if self.ticks_per_beat is not None:
            return TICKS_IN_BEAT / self.ticks_per_beat
        return 1

    def parse_project(self, vsq_project: mido.MidiFile) -> Project:
        self.ticks_per_beat = vsq_project.ticks_per_beat
        self._convert_delta_to_cumulative(vsq_project.tracks)
        tracks_as_text = self.extract_vsq_text_from_meta_events(vsq_project.tracks)
        measure_prefix = self.get_measure_prefix(tracks_as_text[0])
        master_track = vsq_project.tracks[0]
        time_signature_list = self.parse_time_signatures(master_track)
        self.first_bar_length = round(time_signature_list[0].bar_length(self.ticks_per_beat))
        tick_prefix = self.first_bar_length * measure_prefix
        song_tempo_list = self.parse_tempo(master_track, tick_prefix)
        self.synchronizer = TimeSynchronizer(song_tempo_list)
        return Project(
            song_tempo_list=song_tempo_list,
            time_signature_list=time_signature_list,
            track_list=[
                self.parse_track(text, i + 1, tick_prefix) for i, text in enumerate(tracks_as_text)
            ],
        )

    @staticmethod
    def get_measure_prefix(text: str) -> int:
        master_parser = configparser.ConfigParser()
        try:
            master_parser.read_string(text)
        except configparser.Error:
            master_parser.read_string(text.rsplit("\n", 1)[0])
        return master_parser.getint("Master", "PreMeasure", fallback=1)

    @staticmethod
    def extract_vsq_text_from_meta_events(
        tracks: list[mido.MidiTrack],
    ) -> list[str]:
        return [
            text
            for track in tracks
            if (
                text := "".join(
                    event.text.removeprefix("DM:").partition(":")[-1]
                    for event in track
                    if isinstance(event, mido.MetaMessage) and event.type == "text"
                )
            )
        ]

    @staticmethod
    def _convert_delta_to_cumulative(tracks: list[mido.MidiTrack]) -> None:
        for track in tracks:
            tick = 0
            for event in track:
                event.time += tick
                tick = event.time

    def parse_time_signatures(self, master_track: mido.MidiTrack) -> list[TimeSignature]:
        time_signature_changes: list[TimeSignature] = []

        # traversing
        prev_ticks = 0
        measure = 0
        for event in master_track:
            if event.type == "time_signature":
                tick_in_full_note = (
                    time_signature_changes[-1].bar_length(self.ticks_per_beat)
                    if len(time_signature_changes)
                    else 4 * self.ticks_per_beat
                )
                tick = event.time
                measure += (tick - prev_ticks) / tick_in_full_note
                ts_obj = TimeSignature(
                    bar_index=max(math.floor(measure), 0),
                    numerator=event.numerator,
                    denominator=event.denominator,
                )
                time_signature_changes.append(ts_obj)
                prev_ticks = tick
        if not time_signature_changes:
            time_signature_changes.append(TimeSignature(bar_index=0, numerator=4, denominator=4))
        return time_signature_changes

    def parse_tempo(self, master_track: mido.MidiTrack, tick_prefix: int) -> list[SongTempo]:
        tempos = []

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
                        tempos.append(SongTempo(position=tick - tick_prefix, bpm=tempo))
        if not tempos:
            tempos.append(SongTempo(position=0))
        return tempos

    def parse_track(self, text: str, track_index: int, tick_prefix: int) -> SingingTrack:
        vsq_track = configparser.ConfigParser()
        try:
            vsq_track.read_string(text)
        except configparser.Error:
            vsq_track.read_string(text.rsplit("\n", 1)[0])
        singer_name = ""
        if (
            singer_icon_key := next(
                (
                    value.get("iconhandle")
                    for key, value in vsq_track.items()
                    if key.startswith("ID#") and value.get("type") == "Singer"
                ),
                None,
            )
        ) is not None:
            singer_name = vsq_track.get(singer_icon_key, "ids", fallback="")
        singing_track = SingingTrack(
            ai_singer_name=singer_name,
            title=vsq_track.get("Common", "Name", fallback=f"Track {track_index}"),
            note_list=self.parse_notes(vsq_track, tick_prefix)
            if vsq_track.has_section("EventList")
            else [],
        )
        if self.options.import_pitch and (
            pitch := self.parse_pitch(vsq_track, singing_track.note_list, tick_prefix)
        ):
            singing_track.edited_params.pitch = pitch
        return singing_track

    def parse_pitch(
        self,
        vsq_track: configparser.ConfigParser,
        note_list: list[Note],
        tick_prefix: int,
    ) -> Optional[ParamCurve]:
        pit: list[ControllerEvent] = []
        pbs: list[ControllerEvent] = []
        if vsq_track.has_section("PitchBendBPList"):
            pit.extend(
                ControllerEvent(
                    pos=int(key) - tick_prefix,
                    value=int(value),
                )
                for key, value in vsq_track["PitchBendBPList"].items()
            )
        if vsq_track.has_section("PitchBendSensBPList"):
            pbs.extend(
                ControllerEvent(
                    pos=int(key) - tick_prefix,
                    value=int(value),
                )
                for key, value in vsq_track["PitchBendSensBPList"].items()
            )
        return pitch_from_vocaloid_parts(
            [
                VocaloidPartPitchData(
                    start_pos=0,
                    pit=pit,
                    pbs=pbs,
                )
            ],
            self.synchronizer,
            note_list,
            self.first_bar_length,
        )

    def parse_notes(self, vsq_track: configparser.ConfigParser, tick_prefix: int) -> list[Note]:
        notes = []
        for tick_str, event_key in vsq_track["EventList"].items():
            tick = int(tick_str) - tick_prefix
            if event_key.startswith("ID#"):
                vsq_note = vsq_track[event_key]
                if (
                    vsq_note["type"] == "Anote"
                    and (length := vsq_note.getint("length"))
                    and (key := vsq_note.getint("note#"))
                ):
                    lyric_handle = vsq_note.get("lyrichandle", fallback="")
                    lyric_value, phoneme_value = vsq_track.get(
                        lyric_handle, "L0", fallback=","
                    ).split(",")[:2]
                    if BREATH_PATTERN.fullmatch(phoneme_value.strip('"')) is not None:
                        if self.options.breath == BreathOption.IGNORE:
                            continue
                        else:
                            lyric_value = phoneme_value
                    notes.append(
                        Note(
                            start_pos=tick,
                            length=length,
                            key_number=key,
                            lyric=lyric_value.strip('"'),
                            pronunciation=None,
                        )
                    )
        return notes
