import aristaproto
from pydantic.dataclasses import dataclass


class PluginCategory(aristaproto.Enum):
    INPUT = 0
    OUTPUT = 1
    MIDDLEWARE = 2


class ConversionMode(aristaproto.Enum):
    DIRECT = 0
    SPLIT = 1
    MERGE = 2


@dataclass
class PluginInfo(aristaproto.Message):
    identifier: str = aristaproto.string_field(1)
    name: str = aristaproto.string_field(2)
    version: str = aristaproto.string_field(3)
    description: str = aristaproto.string_field(4)
    author: str = aristaproto.string_field(5)
    website: str = aristaproto.string_field(6)
    json_schema: str = aristaproto.string_field(7)
    file_format: str = aristaproto.string_field(8)
    """additional fields for io plugins"""
    suffixes: list[str] = aristaproto.string_field(9)
    icon_base64: str = aristaproto.string_field(10)


@dataclass
class PluginInfosRequest(aristaproto.Message):
    category: "PluginCategory" = aristaproto.enum_field(1)
    language: str = aristaproto.string_field(2)


@dataclass
class PluginInfosResponse(aristaproto.Message):
    values: list["PluginInfo"] = aristaproto.message_field(1)


@dataclass
class ConversionGroup(aristaproto.Message):
    group_id: str = aristaproto.string_field(1)
    file_contents: list[bytes] = aristaproto.bytes_field(2)


@dataclass
class ConversionRequest(aristaproto.Message):
    input_format: str = aristaproto.string_field(1)
    output_format: str = aristaproto.string_field(2)
    mode: "ConversionMode" = aristaproto.enum_field(3)
    groups: list["ConversionGroup"] = aristaproto.message_field(4)
    input_options: str = aristaproto.string_field(5)
    output_options: str = aristaproto.string_field(6)
    middleware_options: dict[str, str] = aristaproto.map_field(
        7, aristaproto.TYPE_STRING, aristaproto.TYPE_STRING
    )


@dataclass
class SingleConversionResult(aristaproto.Message):
    success: bool = aristaproto.bool_field(1)
    file_contents: list[bytes] = aristaproto.bytes_field(2)
    error_message: str = aristaproto.string_field(3)
    warning_message: str = aristaproto.string_field(4)


@dataclass
class ConversionResponse(aristaproto.Message):
    group_results: dict[str, "SingleConversionResult"] = aristaproto.map_field(
        1, aristaproto.TYPE_STRING, aristaproto.TYPE_MESSAGE
    )
