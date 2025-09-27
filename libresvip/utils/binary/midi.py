from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO, Final

from construct import (
    Array,
    Byte,
    BytesInteger,
    Computed,
    Const,
    Construct,
    ExprAdapter,
    FocusedSeq,
    GreedyBytes,
    GreedyRange,
    IfThenElse,
    Int8ub,
    Int16sb,
    Int16ub,
    Int32ub,
    IntegerError,
    Peek,
    Prefixed,
    Rebuild,
    Struct,
    Switch,
    len_,
    stream_read,
    stream_write,
    this,
)
from construct import Enum as CSEnum
from construct import Path as CSPath
from construct.lib import byte2int, integertypes

from . import singleton

if TYPE_CHECKING:
    from construct_typed import Context

PITCH_MIN_VALUE: Final[int] = -8192
PITCH_MAX_VALUE: Final[int] = 8191
DEFAULT_PITCH_BEND_SENSITIVITY: Final[int] = 2
MAX_PITCH_BEND_SENSITIVITY: Final[int] = 24


@singleton
class VarIntBE(Construct):
    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> int:
        acc = []
        while True:
            b = byte2int(stream_read(stream, 1, path))
            acc.append(b & 0x7F)
            if b & 0x80 == 0:
                break
        num = 0
        for b in acc:
            num = (num << 7) | b
        return num

    def _build(self, obj: int, stream: BinaryIO, context: Context, path: CSPath) -> int:
        if not isinstance(obj, integertypes):
            msg = f"value {obj} is not an integer"
            raise IntegerError(msg, path=path)
        if obj < 0:
            msg = f"VarIntBE cannot build from negative number {obj}"
            raise IntegerError(msg, path=path)
        # from https://github.com/musx-admin/musx/blob/main/musx/midi/midimsg.py
        x = obj
        b = bytearray()
        for i in range(21, 0, -7):
            if x >= (1 << i):
                b.append(((x >> i) & 0x7F) | 0x80)
        b.append(x & 0x7F)
        stream_write(stream, bytes(b), len(b), path)
        return obj

    def _emitprimitivetype(self, ksy: object, bitwise: bool) -> str:
        return "vlq_base128_be"


def remember_last(obj: int, ctx: Context) -> None:
    """Stores the last-seen status in the parsing context.
    Bit of a hack to make running status support work.
    Adapted from https://github.com/mik3y/pymidi/blob/main/pymidi/packets.py
    """
    setattr(ctx._root, "_last_status", obj)


# bpm conversion functions from mido
def bpm2tempo(bpm: float) -> int:
    """Convert beats per minute to MIDI file tempo.

    Returns microseconds per beat as an integer::

        240 => 250000
        120 => 500000
        60 => 1000000
    """
    # One minute is 60 million microseconds.
    return round((60 * 1000000) / bpm)


def tempo2bpm(tempo: int) -> float:
    """Convert MIDI file tempo to BPM.

    Returns BPM as an integer or float::

        250000 => 240
        500000 => 120
        1000000 => 60
    """
    # One minute is 60 million microseconds.
    return (60 * 1000000) / tempo


MIDITypeEnum = CSEnum(Int16ub, FORMAT_0=0, FORMAT_1=1, FORMAT_2=2)

MIDIMessage = Struct(
    time=VarIntBE,
    __next=Peek(Int8ub),
    status=IfThenElse(
        this.__next & 0x80,
        Byte * remember_last,
        Computed(lambda ctx: ctx._root._last_status),
    ),
    detail=Switch(
        lambda this: this.status,
        {
            0xFF: Struct(
                type=Computed("meta"),
                event_type=Int8ub,
                data=Prefixed(
                    VarIntBE,
                    Switch(
                        this.event_type,
                        {
                            0x00: Struct(
                                type=Computed("sequence_number"),
                                number=Int16ub,
                            ),
                            0x01: Struct(
                                type=Computed("text"),
                                text=GreedyBytes,
                            ),
                            0x02: Struct(
                                type=Computed("copyright"),
                                text=GreedyBytes,
                            ),
                            0x03: Struct(
                                type=Computed("track_name"),
                                name=GreedyBytes,
                            ),
                            0x04: Struct(
                                type=Computed("instrument_name"),
                                name=GreedyBytes,
                            ),
                            0x05: Struct(
                                type=Computed("lyrics"),
                                text=GreedyBytes,
                            ),
                            0x06: Struct(
                                type=Computed("marker"),
                                text=GreedyBytes,
                            ),
                            0x07: Struct(
                                type=Computed("cue_point"),
                                text=GreedyBytes,
                            ),
                            0x08: Struct(
                                type=Computed("program_name"),
                                text=GreedyBytes,
                            ),
                            0x09: Struct(
                                type=Computed("device_name"),
                                name=GreedyBytes,
                            ),
                            0x20: Struct(
                                type=Computed("channel_prefix"),
                                channel=GreedyBytes,
                            ),
                            0x21: Struct(
                                type=Computed("midi_port"),
                                port=GreedyBytes,
                            ),
                            0x2F: Struct(
                                type=Computed("end_of_track"),
                            ),
                            0x51: Struct(
                                type=Computed("set_tempo"),
                                tempo=BytesInteger(3),
                            ),
                            0x54: Struct(
                                type=Computed("smpte_offset"),
                                _frame_rate_and_hours=Int8ub,
                                frame_rate=Computed(lambda ctx: ctx._frame_rate_and_hours >> 6),
                                hours=Computed(lambda ctx: ctx._frame_rate_and_hours & 0x3F),
                                minutes=Int8ub,
                                seconds=Int8ub,
                                frames=Int8ub,
                                sub_frames=Int8ub,
                            ),
                            0x58: Struct(
                                type=Computed("time_signature"),
                                numerator=Int8ub,
                                denominator=ExprAdapter(
                                    Int8ub,
                                    encoder=lambda obj, context: obj.bit_length() - 1,
                                    decoder=lambda obj, context: 1 << obj,
                                ),
                                clocks_per_click=Int8ub,
                                notated_32nd_notes_per_quarter=Int8ub,
                            ),
                            0x59: Struct(
                                type=Computed("key_signature"),
                                key=Int8ub,
                                scale=Int8ub,
                            ),
                            0x7F: Struct(
                                type=Computed("sequencer_specific"),
                                data=GreedyBytes,
                            ),
                        },
                    ),
                ),
            ),
            0xF0: Struct(
                type=Computed("sysex"),
                data=Prefixed(VarIntBE, GreedyBytes),
            ),
            0xF7: Struct(
                type=Computed("escape_sequence"),
                data=Prefixed(VarIntBE, GreedyBytes),
            ),
        },
        default=Struct(
            type=Computed("channel"),
            channel=Computed(lambda this: this._.status & 0x0F),
            data=Switch(
                lambda this: this._.status & 0xF0,
                {
                    0x80: Struct(
                        note=Int8ub,
                        velocity=Int8ub,
                        type=Computed("note_off"),
                    ),
                    0x90: Struct(
                        type=Computed("note_on"),
                        note=Int8ub,
                        velocity=Int8ub,
                    ),
                    0xA0: Struct(
                        type=Computed("polytouch"),
                        note=Int8ub,
                        value=Int8ub,
                    ),
                    0xB0: Struct(
                        type=Computed("control_change"),
                        control=Int8ub,
                        value=Int8ub,
                    ),
                    0xC0: Struct(
                        type=Computed("program_change"),
                        program=Int8ub,
                    ),
                    0xD0: Struct(
                        type=Computed("aftertouch"),
                        value=Int8ub,
                    ),
                    0xE0: Struct(
                        type=Computed("pitchwheel"),
                        pitch=ExprAdapter(
                            Int16ub,
                            encoder=lambda obj, context: obj - PITCH_MIN_VALUE,
                            decoder=lambda obj, context: obj + PITCH_MIN_VALUE,
                        ),
                    ),
                },
            ),
        ),
    ),
)
MIDITrack = FocusedSeq(
    "messages",
    magic=Const(b"MTrk"),
    messages=Prefixed(Int32ub, GreedyRange(MIDIMessage)),
)
MIDIFile = Struct(
    magic=Const(b"MThd"),
    header_length=Const(6, Int32ub),
    type=MIDITypeEnum,
    track_count=Rebuild(Int16ub, len_(this.tracks)),
    ticks_per_beat=Int16sb,
    tracks=Array(this.track_count, MIDITrack),
)
