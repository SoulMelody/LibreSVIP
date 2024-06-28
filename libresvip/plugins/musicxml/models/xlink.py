from enum import Enum
from typing import Optional

from xsdata_pydantic.fields import field

from libresvip.model.base import BaseModel

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


class Href(BaseModel):
    class Meta:
        name = "href"
        namespace = XLINK_NS

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Role(BaseModel):
    class Meta:
        name = "role"
        namespace = XLINK_NS

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Title(BaseModel):
    class Meta:
        name = "title"
        namespace = XLINK_NS

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )


class Actuate(BaseModel):
    class Meta:
        name = "actuate"
        namespace = XLINK_NS

    value: Optional[ActuateValue] = field(default=None)


class Show(BaseModel):
    class Meta:
        name = "show"
        namespace = XLINK_NS

    value: Optional[ShowValue] = field(default=None)


class TypeType(BaseModel):
    class Meta:
        name = "type"
        namespace = XLINK_NS

    value: Optional[TypeValue] = field(default=None)
