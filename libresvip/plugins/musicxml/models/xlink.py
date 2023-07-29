from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

XLINK_NS = "http://www.w3.org/1999/xlink"


class ActuateValue(Enum):
    ON_REQUEST = "onRequest"
    ON_LOAD = "onLoad"
    OTHER = "other"
    NONE = "none"


class ShowValue(Enum):
    NEW = "new"
    REPLACE = "replace"
    EMBED = "embed"
    OTHER = "other"
    NONE = "none"


class TypeValue(Enum):
    SIMPLE = "simple"


@dataclass
class Href:
    class Meta:
        name = "href"
        namespace = XLINK_NS

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class Role:
    class Meta:
        name = "role"
        namespace = XLINK_NS

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class Title:
    class Meta:
        name = "title"
        namespace = XLINK_NS

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


@dataclass
class Actuate:
    class Meta:
        name = "actuate"
        namespace = XLINK_NS

    value: Optional[ActuateValue] = field(default=None)


@dataclass
class Show:
    class Meta:
        name = "show"
        namespace = XLINK_NS

    value: Optional[ShowValue] = field(default=None)


@dataclass
class TypeType:
    class Meta:
        name = "type"
        namespace = XLINK_NS

    value: Optional[TypeValue] = field(default=None)
