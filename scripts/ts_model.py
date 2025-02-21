from enum import Enum

from pydantic import BaseModel
from xsdata_pydantic.fields import field


class Byte(BaseModel):
    class Meta:
        name = "byte"

    value: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Dependency(BaseModel):
    class Meta:
        name = "dependency"

    catalog: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Location(BaseModel):
    class Meta:
        name = "location"

    filename: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    line: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MessageNumerus(Enum):
    YES = "yes"
    NO = "no"


class NumerusformVariants(Enum):
    YES = "yes"
    NO = "no"


class TranslationType(Enum):
    UNFINISHED = "unfinished"
    VANISHED = "vanished"
    OBSOLETE = "obsolete"


class TranslationVariants(Enum):
    YES = "yes"
    NO = "no"


class Userdata(BaseModel):
    class Meta:
        name = "userdata"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class ByteType(BaseModel):
    class Meta:
        name = "byte-type"

    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "byte",
                    "type": Byte,
                },
            ),
        },
    )


class Dependencies(BaseModel):
    class Meta:
        name = "dependencies"

    dependency: list[Dependency] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


class Comment(ByteType):
    class Meta:
        name = "comment"


class ExtraSomething(ByteType):
    class Meta:
        name = "extra-something"


class Extracomment(ByteType):
    class Meta:
        name = "extracomment"


class Lengthvariant(ByteType):
    class Meta:
        name = "lengthvariant"


class Name(ByteType):
    class Meta:
        name = "name"


class Oldcomment(ByteType):
    class Meta:
        name = "oldcomment"


class Oldsource(ByteType):
    class Meta:
        name = "oldsource"


class Source(ByteType):
    class Meta:
        name = "source"


class Translatorcomment(ByteType):
    class Meta:
        name = "translatorcomment"


class Numerusform(BaseModel):
    class Meta:
        name = "numerusform"

    variants: NumerusformVariants = field(
        default=NumerusformVariants.NO,
        metadata={
            "type": "Attribute",
        },
    )
    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "byte",
                    "type": Byte,
                },
                {
                    "name": "lengthvariant",
                    "type": Lengthvariant,
                },
            ),
        },
    )


class Translation(BaseModel):
    class Meta:
        name = "translation"

    type_value: TranslationType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    variants: TranslationVariants = field(
        default=TranslationVariants.NO,
        metadata={
            "type": "Attribute",
        },
    )
    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "byte",
                    "type": Byte,
                },
                {
                    "name": "numerusform",
                    "type": Numerusform,
                },
                {
                    "name": "lengthvariant",
                    "type": Lengthvariant,
                },
            ),
        },
    )


class Message(BaseModel):
    class Meta:
        name = "message"

    location: list[Location] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    source: Source | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    oldsource: Oldsource | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    comment: Comment | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    oldcomment: Oldcomment | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    extracomment: Extracomment | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    translatorcomment: Translatorcomment | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    translation: Translation | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    userdata: Userdata | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    extra_something: list[ExtraSomething] = field(
        default_factory=list,
        metadata={
            "name": "extra-something",
            "type": "Element",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    numerus: MessageNumerus = field(
        default=MessageNumerus.NO,
        metadata={
            "type": "Attribute",
        },
    )


class Context(BaseModel):
    class Meta:
        name = "context"

    name: Name = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    comment: Comment | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    message: list[Message] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    encoding: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Ts(BaseModel):
    class Meta:
        name = "TS"

    extra_something: list[ExtraSomething] = field(
        default_factory=list,
        metadata={
            "name": "extra-something",
            "type": "Element",
        },
    )
    dependencies: Dependencies | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    context: list[Context] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    message: list[Message] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    version: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    sourcelanguage: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
