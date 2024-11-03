# Yet another MS-NRBF parser and serializer for Python
# Special thanks: netfleece, pypdn, https://github.com/gurnec/Undo_FFG
import abc
import decimal
import threading
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Any, BinaryIO, Union

from construct import (
    Adapter,
    BitsInteger,
    BitStruct,
    Byte,
    BytesInteger,
    Computed,
    Const,
    Construct,
    Container,
    ExprAdapter,
    Flag,
    Float32l,
    Float64l,
    If,
    IfThenElse,
    Int8sl,
    Int8ul,
    Int16sl,
    Int16ul,
    Int64sl,
    Int64ul,
    LazyBound,
    PascalString,
    PrefixedArray,
    RepeatUntil,
    SizeofError,
    Struct,
    Switch,
    this,
)
from construct import Enum as CSEnum
from construct import Path as CSPath
from construct_typed import Context
from typing_extensions import Never

Int32ul = BytesInteger(4, swapped=True)
Int32sl = BytesInteger(4, swapped=True, signed=True)


class TimeSpanAdapter(Adapter):
    def _encode(self, obj: timedelta, context: Context, path: CSPath) -> int:
        return int(obj.total_seconds() * 10000000)

    def _decode(self, obj: int, context: Context, path: CSPath) -> timedelta:
        return timedelta(microseconds=obj / 10)


TimeSpan = TimeSpanAdapter(Int64ul)

DateTimeBitStruct = BitStruct(
    "ticks" / BitsInteger(62),
    "kind" / BitsInteger(2),
)


class DateTimeAdapter(Adapter):
    def _encode(self, obj: datetime, context: Context, path: CSPath) -> bytes:
        if obj.tzinfo is None:
            kind = 0
        elif obj.tzinfo.utcoffset(obj) == timedelta(0):
            kind = 1
        else:
            kind = 2
        ticks = (obj - datetime(1, 1, 1, tzinfo=timezone.utc)).total_seconds() * 10000000
        return DateTimeBitStruct.build({"ticks": ticks, "kind": kind})

    def _decode(self, obj: Container, context: Context, path: CSPath) -> datetime:
        date_time = datetime(1, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=obj.ticks / 10)
        if obj.kind == 1:
            date_time = date_time.replace(tzinfo=timezone.utc)
        elif obj.kind == 2:
            local_timezone = datetime.now(tz=timezone.utc).astimezone().tzinfo
            date_time = date_time.replace(tzinfo=local_timezone)
        return date_time


DateTime = DateTimeAdapter(DateTimeBitStruct)


class Null(Construct):
    def _sizeof(self, context: Context, path: CSPath) -> int:
        return 0

    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> None:
        return None

    def _build(self, obj: Container, stream: BinaryIO, context: Context, path: CSPath) -> None:
        pass


class Utf8CodePoint(Construct):
    def _sizeof(self, context: Context, path: CSPath) -> Never:
        msg = "Utf8CodePoint has no static size"
        raise SizeofError(msg)

    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> str:
        byte = stream.read(1)
        if not byte:
            raise EOFError
        b = ord(byte)
        if b & 0x80 == 0:
            length = 1
        elif b & 0xE0 == 0xC0:
            length = 2
        elif b & 0xF0 == 0xE0:
            length = 3
        elif b & 0xF8 == 0xF0:
            length = 4
        else:
            msg = "Invalid UTF-8 code point"
            raise ValueError(msg)
        return (byte + stream.read(length - 1)).decode("utf-8")

    def _build(
        self,
        obj: Union[str, bytes],
        stream: BinaryIO,
        context: Context,
        path: CSPath,
    ) -> bytes:
        if isinstance(obj, str):
            obj = obj.encode("utf-8")
        stream.write(obj)
        return obj


class LengthPrefixedString(Construct):
    def _sizeof(self, context: Context, path: CSPath) -> Never:
        msg = "LengthPrefixedString has no static size"
        raise SizeofError(msg)

    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> str:
        length = 0
        shift = 0
        for i in range(5):
            byte = stream.read(1)
            if not byte:
                raise EOFError
            b = ord(byte)
            length += (b & ~0x80) << shift
            shift += 7
            if not b & 0x80:
                break
        else:
            msg = "Invalid length-prefixed string"
            raise ValueError(msg)
        content = stream.read(length)
        return content.decode("utf-8")

    def _build(
        self,
        obj: Union[str, bytes],
        stream: BinaryIO,
        context: Context,
        path: CSPath,
    ) -> bytes:
        if isinstance(obj, str):
            obj = obj.encode("utf-8")
        length = len(obj)
        while length > 0x7F:
            stream.write(bytes(((length & 0x7F) | 0x80,)))
            length >>= 7
        stream.write(bytes((length,)))
        stream.write(obj)
        return obj


Decimal = ExprAdapter(
    LengthPrefixedString(),
    lambda obj, ctx: decimal.Decimal(obj),
    lambda obj, ctx: str(obj),
)


classes_by_id: dict[int, dict[int, Container]] = defaultdict(dict)
objects_by_id: dict[int, dict[int, Container]] = defaultdict(dict)
libraries_by_id: dict[int, dict[int, str]] = defaultdict(dict)
references_by_id: dict[int, dict[int, Container]] = defaultdict(dict)


class RegistryAdapter(Adapter, abc.ABC):
    def _encode(self, obj: Container, context: Context, path: CSPath) -> Any:
        return obj


class ClassRegistryAdapter(RegistryAdapter):
    def _decode(self, obj: Container, context: Context, path: CSPath) -> Any:
        classes_by_id[threading.get_ident()][obj.class_info.object_id] = obj
        return obj


class ObjectRegistryAdapter(RegistryAdapter):
    def _decode(self, obj: Container, context: Context, path: CSPath) -> Any:
        if obj.get("array_info", None):
            objects_by_id[threading.get_ident()][obj.array_info.object_id] = obj
        else:
            objects_by_id[threading.get_ident()][obj.object_id] = obj
        return obj


class LibraryRegistryAdapter(RegistryAdapter):
    def _decode(self, obj: Container, context: Context, path: CSPath) -> Any:
        libraries_by_id[threading.get_ident()][obj.library_id] = obj.library_name
        return obj


class MemberReferenceAdapter(RegistryAdapter):
    def _decode(self, obj: Container, context: Context, path: CSPath) -> Any:
        ref_cache = references_by_id[threading.get_ident()]
        if obj.id_ref not in ref_cache:
            result = {"id_ref": obj.id_ref, "real_obj": None}
            ref_cache[obj.id_ref] = result
        return ref_cache[obj.id_ref]


PrimitiveTypeEnum = CSEnum(
    Byte,
    Boolean=1,
    Byte=2,
    Char=3,
    Decimal=5,
    Double=6,
    Int16=7,
    Int32=8,
    Int64=9,
    SByte=10,
    Single=11,
    TimeSpan=12,
    DateTime=13,
    UInt16=14,
    UInt32=15,
    UInt64=16,
    Null=17,
    String=18,
)

RecordTypeEnum = CSEnum(
    Byte,
    SerializedStreamHeader=0,
    ClassWithId=1,
    SystemClassWithMembers=2,
    ClassWithMembers=3,
    SystemClassWithMembersAndTypes=4,
    ClassWithMembersAndTypes=5,
    BinaryObjectString=6,
    BinaryArray=7,
    MemberPrimitiveTyped=8,
    MemberReference=9,
    ObjectNull=10,
    MessageEnd=11,
    BinaryLibrary=12,
    ObjectNullMultiple256=13,
    ObjectNullMultiple=14,
    ArraySinglePrimitive=15,
    ArraySingleObject=16,
    ArraySingleString=17,
    MethodCall=21,
    MethodReturn=22,
)

BinaryTypeEnum = CSEnum(
    Byte,
    Primitive=0,
    String=1,
    Object=2,
    SystemClass=3,
    Class=4,
    ObjectArray=5,
    StringArray=6,
    PrimitiveArray=7,
)

BinaryArrayTypeEnum = CSEnum(
    Byte,
    Single=0,
    Jagged=1,
    Rectangular=2,
    SingleOffset=3,
    JaggedOffset=4,
    RectangularOffset=5,
)

MessageFlagsEnum = CSEnum(
    Int32ul,
    NoArgs=0x00000001,
    ArgsInline=0x00000002,
    ArgsIsArray=0x00000004,
    ArgsInArray=0x00000008,
    NoContext=0x00000010,
    ContextInline=0x00000020,
    ContextInArray=0x00000040,
    MethodSignatureInArray=0x00000080,
    PropertiesInArray=0x00000100,
    NoReturnValue=0x00000200,
    ReturnValueVoid=0x00000400,
    ReturnValueInline=0x00000800,
    ReturnValueInArray=0x00001000,
    ExceptionInArray=0x00002000,
    GenericMethod=0x00008000,
)

PrimitiveType = partial(
    Switch,
    cases={
        "Boolean": Flag,
        "Byte": Int8ul,
        "Char": Utf8CodePoint,
        "Decimal": Decimal,
        "Double": Float64l,
        "Int16": Int16sl,
        "Int32": Int32sl,
        "Int64": Int64sl,
        "SByte": Int8sl,
        "Single": Float32l,
        "TimeSpan": TimeSpan,
        "DateTime": DateTime,
        "UInt16": Int16ul,
        "UInt32": Int32ul,
        "UInt64": Int64ul,
        "Null": Null(),
        "String": LengthPrefixedString(),
    },
)

ArrayInfo = Struct(
    "object_id" / Int32sl,
    "length" / Int32sl,
)

ClassTypeInfo = Struct(
    "type_name" / LengthPrefixedString(),
    "library_id" / Int32sl,
)

ClassInfo = Struct(
    "object_id" / Int32sl,
    "name" / LengthPrefixedString(),
    "member_count" / Int32sl,
    "member_names" / LengthPrefixedString()[this.member_count],
)

SerializedStreamHeader = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.SerializedStreamHeader),
    "root_id" / Int32sl,
    "header_id" / Int32sl,
    "major_version" / Int32sl,
    "minor_version" / Int32sl,
)

MemberValue = Struct(
    "value" / LazyBound(lambda: Record),
)

SystemClassWithMembers = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.SystemClassWithMembers),
    "class_info" / ClassInfo,
    "member_values" / MemberValue[this.class_info.member_count],
)

ClassWithMembers = ClassRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.ClassWithMembers),
        "class_info" / ClassInfo,
        "library_id" / Int32sl,
        "member_values" / MemberValue[this.class_info.member_count],
    )
)


BinaryType = partial(
    Switch,
    cases={
        "Primitive": PrimitiveTypeEnum,
        "String": Null(),
        "Object": Null(),
        "SystemClass": LengthPrefixedString(),
        "Class": ClassTypeInfo,
        "ObjectArray": Null(),
        "StringArray": Null(),
        "PrimitiveArray": PrimitiveTypeEnum,
    },
)


MemberTypeAddtionalInfo = Struct(
    "binary_type_enum" / Computed(lambda this: this._.binary_type_enums[this._index]),
    "info" / BinaryType(lambda this: this.binary_type_enum),
)


MemberTypeInfo = Struct(
    "binary_type_enums" / BinaryTypeEnum[this._.class_info.member_count],
    "additional_infos" / MemberTypeAddtionalInfo[this._.class_info.member_count],
)


MemberValueWithType = Struct(
    "binary_type_enum"
    / Computed(lambda this: (this._.member_type_info["binary_type_enums"][this._._index])),
    "value"
    / Switch(
        lambda this: this.binary_type_enum,
        {
            "Primitive": PrimitiveType(
                lambda this: this._.member_type_info["additional_infos"][this._._index]["info"]
            ),
        },
        default=LazyBound(lambda: Record),
    ),
)


SystemClassWithMembersAndTypes = ClassRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.SystemClassWithMembersAndTypes),
        "class_info" / ClassInfo,
        "member_type_info" / MemberTypeInfo,
        "member_values" / MemberValueWithType[this.class_info.member_count],
    )
)

ClassWithMembersAndTypes = ClassRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.ClassWithMembersAndTypes),
        "class_info" / ClassInfo,
        "member_type_info" / MemberTypeInfo,
        "library_id" / Int32sl,
        "member_values" / MemberValueWithType[this.class_info.member_count],
    )
)

ClassWithId = ObjectRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.ClassWithId),
        "object_id" / Int32sl,
        "metadata_id" / Int32sl,
        "class_info"
        / Computed(
            lambda this: (classes_by_id[threading.get_ident()][this.metadata_id]["class_info"])
        ),
        "member_type_info"
        / Computed(
            lambda this: (
                classes_by_id[threading.get_ident()][this.metadata_id].get("member_type_info", None)
            )
        ),
        "member_values"
        / IfThenElse(
            lambda this: this.member_type_info,
            MemberValueWithType[this.class_info.member_count],
            MemberValue[this.class_info.member_count],
        ),
    )
)

BinaryObjectString = ObjectRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.BinaryObjectString),
        "object_id" / Int32sl,
        "value" / LengthPrefixedString(),
    )
)

BinaryArray = ObjectRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.BinaryArray),
        "object_id" / Int32sl,
        "binary_array_type_enum" / BinaryArrayTypeEnum,
        "rank" / Int32sl,
        "lengths" / Int32sl[this.rank],
        "lower_bounds"
        / IfThenElse(
            lambda this: str(this.binary_array_type_enum)
            in [
                "SingleOffset",
                "JaggedOffset",
                "RectangularOffset",
            ],
            Int32sl[this.rank],
            Null(),
        ),
        "binary_type_enum" / BinaryTypeEnum,
        "info" / BinaryType(lambda this: (this.binary_type_enum)),
        "member_values"
        / If(
            lambda this: (
                str(this.binary_array_type_enum)
                not in [
                    "Rectangular",
                    "RectangularOffset",
                ]
                and this.rank == 1
                and this.lengths[0] > 0
            ),
            RepeatUntil(
                lambda obj, lst, ctx: (
                    (
                        len(lst)
                        + sum(
                            (x.real_obj.obj.null_count - 1)
                            for x in lst
                            if "obj" in x.real_obj and "null_count" in x.real_obj.obj
                        )
                    )
                    >= obj["total"]
                ),
                Struct(
                    "total" / Computed(lambda this: (this._.lengths[0])),
                    "real_obj"
                    / Switch(
                        lambda this: this._.binary_type_enum,
                        {
                            "Primitive": PrimitiveType(
                                lambda this: this._._.member_type_info.additional_infos[
                                    this._._._index
                                ].info
                            ),
                            "String": LengthPrefixedString(),
                        },
                        default=LazyBound(lambda: Record),
                    ),
                ),
            ),
        ),
        # TODO: implement multidimensional arrays
    )
)

ValueWithCode = Struct(
    "primitive_type_enum" / PrimitiveTypeEnum,
    "value" / PrimitiveType(this.primitive_type_enum),
)

StringValueWithCode = Struct(
    "primitive_type_enum" / Const(PrimitiveTypeEnum.String, Byte),
    "value" / LengthPrefixedString(),
)

ArrayOfValueWithCode = PrefixedArray(Int32sl, ValueWithCode)

MemberPrimitiveTyped = (
    "record_type_enum" / Computed(RecordTypeEnum.MemberPrimitiveTyped),
    "value" / ValueWithCode,
)

MemberReference = MemberReferenceAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.MemberReference),
        "id_ref" / Int32sl,
    )
)

BinaryLibrary = LibraryRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.BinaryLibrary),
        "library_id" / Int32sl,
        "library_name" / LengthPrefixedString(),
    )
)

ObjectNullMultiple256 = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.ObjectNullMultiple256),
    "null_count" / Int8ul,
)

ObjectNullMultiple = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.ObjectNullMultiple),
    "null_count" / Int32sl,
)

ArraySinglePrimitive = ObjectRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.ArraySinglePrimitive),
        "array_info" / ArrayInfo,
        "primitive_type_enum" / PrimitiveTypeEnum,
        "member_values" / PrimitiveType(this.primitive_type_enum)[this.array_info.length],
    )
)

ArraySingleObject = ObjectRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.ArraySingleObject),
        "array_info" / ArrayInfo,
        "member_values" / LazyBound(lambda: Record[this.array_info.length]),
    )
)

ArraySingleString = ObjectRegistryAdapter(
    Struct(
        "record_type_enum" / Computed(RecordTypeEnum.ArraySingleString),
        "array_info" / ArrayInfo,
        "member_values" / LazyBound(lambda: Record[this.array_info.length]),
    )
)

MethodCall = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.MethodCall),
    "flags" / MessageFlagsEnum,
    "method_name" / StringValueWithCode,
    "type_name" / StringValueWithCode,
    "call_context"
    / If(
        this.flags & MessageFlagsEnum.ContextInline,
        StringValueWithCode,
    ),
    "args"
    / If(
        this.flags & MessageFlagsEnum.ArgsInline,
        ArrayOfValueWithCode,
    ),
)

MethodReturn = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.MethodReturn),
    "flags" / MessageFlagsEnum,
    "return_value"
    / If(
        this.flags & MessageFlagsEnum.ReturnValueInline,
        ValueWithCode,
    ),
    "call_context"
    / If(
        this.flags & MessageFlagsEnum.ContextInline,
        StringValueWithCode,
    ),
    "args"
    / If(
        this.flags & MessageFlagsEnum.ArgsInline,
        ArrayOfValueWithCode,
    ),
)


ObjectNull = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.ObjectNull),
)

MessageEnd = Struct(
    "record_type_enum" / Computed(RecordTypeEnum.MessageEnd),
)


Record: Container = Struct(
    "record_type_enum" / RecordTypeEnum,
    "obj"
    / Switch(
        this.record_type_enum,
        {
            "SerializedStreamHeader": SerializedStreamHeader,
            "ClassWithId": ClassWithId,
            "SystemClassWithMembers": SystemClassWithMembers,
            "ClassWithMembers": ClassWithMembers,
            "SystemClassWithMembersAndTypes": SystemClassWithMembersAndTypes,
            "ClassWithMembersAndTypes": ClassWithMembersAndTypes,
            "BinaryObjectString": BinaryObjectString,
            "BinaryArray": BinaryArray,
            "MemberPrimitiveTyped": MemberPrimitiveTyped,
            "MemberReference": MemberReference,
            "ObjectNull": ObjectNull,
            "MessageEnd": MessageEnd,
            "BinaryLibrary": BinaryLibrary,
            "ObjectNullMultiple256": ObjectNullMultiple256,
            "ObjectNullMultiple": ObjectNullMultiple,
            "ArraySinglePrimitive": ArraySinglePrimitive,
            "ArraySingleObject": ArraySingleObject,
            "ArraySingleString": ArraySingleString,
            "MethodCall": MethodCall,
            "MethodReturn": MethodReturn,
        },
    ),
)

RecordStream = RepeatUntil(
    lambda obj, lst, ctx: obj is None or obj["record_type_enum"] == RecordTypeEnum.MessageEnd,
    Record,
)


SVIPFile = Struct(
    "magic" / PascalString(Byte, "utf-8"),
    "version" / PascalString(Byte, "utf-8"),
    "record_stream" / RecordStream,
)
