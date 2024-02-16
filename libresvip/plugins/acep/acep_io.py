import pathlib
from typing import Any

from pydantic import Base64Bytes, Field

from libresvip.core.compat import json, zstd
from libresvip.model.base import BaseModel


class AcepDebug(BaseModel):
    os: str = "windows"
    platform: str = "pc"
    version: str = "10"


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
    acep_file = AcepFile.model_validate_json(src.read_bytes().decode("utf-8"))
    decompressed = zstd.decompress(acep_file.content)
    return json.loads(decompressed)


def compress_ace_studio_project(src: dict[str, Any], target: pathlib.Path) -> None:
    raw_content = json.dumps(src).encode()
    compressed = zstd.compress(raw_content)
    acep_file = AcepFile.model_construct(content=compressed)
    target.write_bytes(
        json.dumps(acep_file.model_dump(mode="json", by_alias=True), separators=(",", ":")).encode(
            "utf-8"
        )
    )
