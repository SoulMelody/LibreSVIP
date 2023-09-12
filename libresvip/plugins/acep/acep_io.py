import pathlib
from typing import Any

import zstandard
from pydantic import Base64Bytes, Field

from libresvip.model.base import BaseModel, json_dumps, json_loads

from .model import AcepDebug


class AcepFile(BaseModel):
    compress_method: str = Field(default="zstd", alias="compressMethod")
    debug_info: AcepDebug = Field(
        default_factory=AcepDebug,
        alias="debugInfo",
    )
    salt: str = ""
    version: int = Field(default=1000)
    content: Base64Bytes


def decompress_ace_studio_project(src: pathlib.Path) -> dict[str, Any]:
    if not isinstance(src, pathlib.Path):
        src = pathlib.Path(src)
    acep_file = AcepFile.model_validate_json(src.read_text())
    decompressed = zstandard.decompress(acep_file.content)
    return json_loads(decompressed)


def compress_ace_studio_project(src: dict[str, Any], target: pathlib.Path) -> None:
    raw_content = json_dumps(src).encode()
    compressed = zstandard.compress(raw_content)
    acep_file = AcepFile.model_construct(content=compressed)
    if not isinstance(target, pathlib.Path):
        target = pathlib.Path(target)
    target.write_text(
        json_dumps(
            acep_file.model_dump(mode="json", by_alias=True), separators=(",", ":")
        )
    )
