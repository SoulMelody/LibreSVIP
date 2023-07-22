import dataclasses
import operator

import mido
import regex as re

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.model.base import (
    Project,
    SingingTrack,
    Track,
)

from .constants import ControlChange
from .midi_pitch import generate_for_midi
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
        mido_obj = mido.MidiFile(charset=self.options.lyric_encoding)
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

    def encode_tracks(self, tracks: list[Track]) -> list[mido.MidiTrack]:
        mido_tracks = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                if (mido_track := self.encode_track(track)) is not None:
                    mido_tracks.append(mido_track)
        return mido_tracks

    def encode_track(self, track: SingingTrack) -> mido.MidiTrack:
        lyrics = [
            note.pronunciation if note.pronunciation is not None else note.lyric
            for note in track.note_list
        ]
        if self.options.remove_symbols:
            lyrics = [re.sub(r"(?!-)\p{punct}", "", lyric) for lyric in lyrics]
        pinyins = get_pinyin_series(lyrics)
        mido_track = mido.MidiTrack()
        mido_track.name = track.title
        for i, note in enumerate(track.note_list):
            if self.options.export_lyrics:
                mido_track.append(
                    mido.MetaMessage(
                        "lyrics",
                        text=(
                            pinyins[i] if self.options.compatible_lyric else lyrics[i]
                        ),
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
        if pitch_data := generate_for_midi(track.edited_params.pitch, track.note_list):
            for pbs_event in pitch_data.pbs:
                msg_time = round(pbs_event.tick / self.tick_rate)
                mido_track.extend([
                    mido.Message(
                        "control_change",
                        control=ControlChange.RPN_MSB.value,
                        value=0,
                        time=msg_time,
                    ),
                    mido.Message(
                        "control_change",
                        control=ControlChange.RPN_LSB.value,
                        value=0,
                        time=msg_time,
                    ),
                    mido.Message(
                        "control_change",
                        control=ControlChange.DATA_ENTRY.value,
                        value=pbs_event.value,
                        time=msg_time,
                    ),
                ])
            for pitch_event in pitch_data.pit:
                mido_track.append(
                    mido.Message(
                        "pitchwheel",
                        pitch=pitch_event.value,
                        time=round(pitch_event.tick / self.tick_rate),
                    )
                )
        mido_track.sort(key=operator.attrgetter("time"))
        if len(mido_track):
            return mido_track
