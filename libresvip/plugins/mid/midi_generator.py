import dataclasses
import operator
from typing import List

import mido
import regex as re

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.model.base import (
    Project,
    SingingTrack,
    Track,
)

from .options import OutputOptions


@dataclasses.dataclass
class MidiGenerator:
    options: OutputOptions
    project: Project = dataclasses.field(init=False)

    @property
    def tick_rate(self):
        if self.options is not None:
            return TICKS_IN_BEAT / self.options.ticks_per_beat
        return 1

    def encode_project(self, project: Project) -> mido.MidiFile:
        mido_obj = mido.MidiFile()
        self.project = project
        mido_obj.ticks_per_beat = self.options.ticks_per_beat
        master_track = mido.MidiTrack()
        self.encode_tempos(master_track)
        self.encode_time_signatures(master_track)
        master_track.sort(key=operator.attrgetter("time"))
        mido_obj.tracks.append(master_track)
        mido_obj.tracks.extend(self.encode_tracks(project.track_list))
        self._convert_cumulative_to_delta(mido_obj.tracks)
        return mido_obj

    @staticmethod
    def _convert_cumulative_to_delta(tracks):
        for track in tracks:
            tick = 0
            for event in track:
                tick, event.time = event.time, event.time - tick

    def encode_tempos(self, master_track: mido.MidiTrack):
        for tempo in self.project.song_tempo_list:
            master_track.append(
                mido.MetaMessage(
                    "set_tempo",
                    tempo=mido.bpm2tempo(tempo.bpm),
                    time=round(tempo.position / self.tick_rate),
                )
            )

    def encode_time_signatures(self, master_track: mido.MidiTrack):
        prev_ticks = 0
        for time_signature in self.project.time_signature_list:
            master_track.append(
                mido.MetaMessage(
                    "time_signature",
                    numerator=time_signature.numerator,
                    denominator=time_signature.denominator,
                    time=prev_ticks,
                )
            )
            prev_ticks += round(
                time_signature.bar_index
                * self.options.ticks_per_beat
                * time_signature.numerator
            )

    def encode_tracks(self, tracks: List[Track]) -> List[mido.MidiTrack]:
        mido_tracks = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                mido_track = self.encode_track(track)
                mido_tracks.append(mido_track)
        return mido_tracks

    def encode_track(self, track: SingingTrack) -> mido.MidiTrack:
        lyrics = [
            note.pronunciation if note.pronunciation is not None else note.lyric
            for note in track.note_list
        ]
        if self.options.remove_symbols:
            lyrics = [re.sub(r"\p{punct}", "", lyric) for lyric in lyrics]
        pinyins = get_pinyin_series(lyrics)
        mido_track = mido.MidiTrack()
        mido_track.name = track.title.encode(self.options.lyric_encoding).decode(
            "latin-1"
        )
        for i, note in enumerate(track.note_list):
            if self.options.export_lyrics:
                mido_track.append(
                    mido.MetaMessage(
                        "lyrics",
                        text=(
                            pinyins[i] if self.options.compatible_lyric else lyrics[i]
                        )
                        .encode(
                            self.options.lyric_encoding,
                            errors="ignore",
                        )
                        .decode("latin-1"),
                        time=round(note.start_pos / self.tick_rate),
                    )
                )
            mido_track.append(
                mido.Message(
                    "note_on",
                    note=note.key_number,
                    time=round(note.start_pos / self.tick_rate),
                )
            )
            mido_track.append(
                mido.Message(
                    "note_off",
                    note=note.key_number,
                    time=round(note.end_pos / self.tick_rate),
                )
            )
        # TODO: Add support for pitch bend
        mido_track.sort(key=operator.attrgetter("time"))
        return mido_track
