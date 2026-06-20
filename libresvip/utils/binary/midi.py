from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO, Final

from construct import (
    Byte,
    BytesInteger,
    Computed,
    Const,
    ConstError,
    Construct,
    Container,
    ExprAdapter,
    ExprValidator,
    FocusedSeq,
    GreedyBytes,
    GreedyRange,
    IfThenElse,
    Int8sb,
    Int8ub,
    Int16sb,
    Int16ub,
    Int32ub,
    IntegerError,
    ListContainer,
    Peek,
    Prefixed,
    SizeofError,
    StreamError,
    Struct,
    Switch,
    stream_read,
    stream_write,
    this,
)
from construct import Enum as CSEnum
from construct import Path as CSPath
from construct.lib import byte2int, integertypes

from libresvip.utils.music_math import ratio_to_db

from . import singleton

if TYPE_CHECKING:
    from construct_typed import Context

PITCH_MIN_VALUE: Final[int] = -8192
PITCH_MAX_VALUE: Final[int] = 8191
DEFAULT_PITCH_BEND_SENSITIVITY: Final[int] = 2
MAX_PITCH_BEND_SENSITIVITY: Final[int] = 24
EXPRESSION_CONSTANT: Final[float] = 2.0
MIDI_HEADER_CHUNK: Final[bytes] = b"MThd"
MIDI_TRACK_CHUNK: Final[bytes] = b"MTrk"
MIDI_HEADER_DATA_LENGTH: Final[int] = 6


def cc11_to_db_change(value: float) -> float:
    return ratio_to_db((value / 127) ** EXPRESSION_CONSTANT + 1e-6)


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


PitchBend = ExprValidator(
    ExprAdapter(
        Struct(
            lsb=Int8ub,
            msb=Int8ub,
        ),
        encoder=lambda obj, context: {
            "lsb": (obj - PITCH_MIN_VALUE) & 0x7F,
            "msb": (obj - PITCH_MIN_VALUE) >> 7,
        },
        decoder=lambda obj, context: ((obj.msb << 7) | obj.lsb) + PITCH_MIN_VALUE,
    ),
    lambda obj, context: PITCH_MIN_VALUE <= obj <= PITCH_MAX_VALUE,
)


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
    _next=Peek(Int8ub),
    status=IfThenElse(
        this._next & 0x80,
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
                                frame_rate=Computed(
                                    lambda ctx: (ctx._frame_rate_and_hours >> 5) & 0x03
                                ),
                                hours=Computed(lambda ctx: ctx._frame_rate_and_hours & 0x1F),
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
                                key=Int8sb,
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
                        pitch=PitchBend,
                    ),
                },
            ),
        ),
    ),
)
MIDITrack = FocusedSeq(
    "messages",
    magic=Const(MIDI_TRACK_CHUNK),
    messages=Prefixed(Int32ub, GreedyRange(MIDIMessage)),
)


@singleton
class MIDIFileStruct(Construct):
    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> Container:
        magic = stream_read(stream, 4, path)
        if magic != MIDI_HEADER_CHUNK:
            msg = f"parsing expected {MIDI_HEADER_CHUNK!r} but parsed {magic!r}"
            raise ConstError(msg, path=path)
        header_length = Int32ub._parsereport(stream, context, path)
        if header_length < MIDI_HEADER_DATA_LENGTH:
            msg = f"MIDI header length must be at least {MIDI_HEADER_DATA_LENGTH}"
            raise StreamError(msg, path=path)
        header = stream_read(stream, header_length, path)
        track_count = Int16ub.parse(header[2:4])
        tracks = ListContainer()
        while len(tracks) < track_count:
            chunk_magic = stream_read(stream, 4, path)
            chunk_length = Int32ub._parsereport(stream, context, path)
            chunk_data = stream_read(stream, chunk_length, path)
            if chunk_magic == MIDI_TRACK_CHUNK:
                tracks.append(
                    MIDITrack.parse(
                        chunk_magic + Int32ub.build(chunk_length) + chunk_data,
                    )
                )
        return Container(
            _io=stream,
            magic=magic,
            header_length=header_length,
            type=MIDITypeEnum.parse(header[:2]),
            track_count=track_count,
            ticks_per_beat=Int16sb.parse(header[4:6]),
            tracks=tracks,
        )

    def _build(self, obj: Container, stream: BinaryIO, context: Context, path: CSPath) -> Container:
        tracks = obj["tracks"]
        header = (
            MIDITypeEnum.build(obj["type"])
            + Int16ub.build(len(tracks))
            + Int16sb.build(obj["ticks_per_beat"])
        )
        stream_write(stream, MIDI_HEADER_CHUNK, 4, path)
        stream_write(stream, Int32ub.build(MIDI_HEADER_DATA_LENGTH), 4, path)
        stream_write(stream, header, MIDI_HEADER_DATA_LENGTH, path)
        for track in tracks:
            track_data = MIDITrack.build(track)
            stream_write(stream, track_data, len(track_data), path)
        return obj

    def _sizeof(self, context: Context, path: CSPath) -> int:
        raise SizeofError(path=path)


MIDIFile = MIDIFileStruct
