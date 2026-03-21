import contextlib
import hashlib
import importlib
import pathlib
import sys
from typing import Any

import cbor2
from construct import (
    Byte,
    Bytes,
    Const,
    GreedyBytes,
    Int16ul,
    Int64ul,
    Padding,
    Pointer,
    Prefixed,
    Struct,
    this,
)
from pydantic import Base64Bytes, Field, ValidationInfo, field_validator

from libresvip.core.compat import json
from libresvip.core.exceptions import UnsupportedProjectVersionError
from libresvip.model.base import BaseModel
from libresvip.utils.translation import gettext_lazy as _

from .options import AcepSerialization

try:
    __import__("Cryptodome")
except ImportError:
    with contextlib.suppress(ImportError):
        sys.modules["Cryptodome"] = __import__("Crypto")

for zstd_backend in (
    "compression.zstd",
    "backports.zstd",
    "zstd",
    "pyzstd",
    "zstandard",
    "cramjam",
    "numcodecs.zstd",
):
    with contextlib.suppress(ImportError):
        zstd = importlib.import_module(zstd_backend)
        if zstd_backend == "cramjam":
            zstd = zstd.zstd
        ZSTD_AVAILABLE = True
        break
else:
    ZSTD_AVAILABLE = False

ACEP2_MAGIC = b"ACEP2"
ACEP2_FLAG = 0x01


Acep2Header = Struct(
    "magic" / Const(ACEP2_MAGIC, Bytes(5)),
    "flags" / Const(ACEP2_FLAG, Byte),
    "header_size" / Int16ul,
    "content_offset" / Int64ul,
    "compressed_content_size" / Int64ul,
    "content_size" / Int64ul,
    "encrypted_metadata" / Prefixed(Int16ul, GreedyBytes),
    "metadata_flag" / Const(ACEP2_FLAG, Byte),
    "content_hash" / Bytes(16),
    "padding" / Padding(lambda this: this.content_offset - 51 - len(this.encrypted_metadata)),
)


Acep2File = Struct(
    "header" / Acep2Header,
    "compressed_content"
    / Pointer(
        this.header.content_offset,
        Bytes(this.header.compressed_content_size),
    ),
)


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

    @field_validator("version")
    @classmethod
    def version_validator(cls, value: int, _info: ValidationInfo) -> int:
        if value < 1000 and "Cryptodome" not in sys.modules:
            msg = _("Unsupported project version")
            raise UnsupportedProjectVersionError(msg)
        return value


def decrypt_acep_content_v1(content: bytes) -> bytes:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad

    key_bytes = b"11956722077380335572"
    iv_bytes = b"1103392056537578664"
    key = hashlib.sha256(key_bytes).digest()
    iv = hashlib.md5(iv_bytes).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(content)
    if decrypted.endswith(b"\x00"):
        return unpad(decrypted, AES.block_size, style="iso7816")
    return decrypted


def decrypt_acep_content_v2(content: bytes, salt: str) -> bytes:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad

    iv_bytes = str(int(salt[33:], 16) & 0x49A23B22DD28F042).encode()
    iv = hashlib.md5(iv_bytes).digest()
    key = b"\xb7\x4b\x57\x57\x5f\xb1\x4f\xc7\xec\xa9\x9c\x8b\x82\x53\x10\xfc\x4a\x33\x7b\x83\x7b\x12\x83\xe9\x0e\xe0\xef\x02\x20\x1c\x91\x12"
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(content)
    if decrypted.endswith(b"\x00"):
        return unpad(decrypted, AES.block_size, style="iso7816")
    return decrypted


def decompress_ace_studio_project(src: pathlib.Path) -> dict[str, Any]:
    content = src.read_bytes()
    if content[:5] == ACEP2_MAGIC:
        result = Acep2File.parse(content)
        decompressed = zstd.decompress(result.compressed_content)
        if not isinstance(decompressed, bytes):
            decompressed = bytes(decompressed)
        return cbor2.loads(decompressed)
    else:
        acep_file = AcepFile.model_validate_json(content.decode("utf-8"))
        if acep_file.version == 1:
            content = decrypt_acep_content_v1(acep_file.content)
        elif acep_file.version == 2:
            content = decrypt_acep_content_v2(acep_file.content, acep_file.salt)
        else:
            content = acep_file.content
        decompressed = zstd.decompress(content)
        if not isinstance(decompressed, bytes):
            decompressed = bytes(decompressed)
        return json.loads(decompressed)


def compress_ace_studio_project(
    src: dict[str, Any], target: pathlib.Path, serialization: AcepSerialization
) -> None:
    if serialization == AcepSerialization.JSON:
        raw_content = json.dumps(src).encode()
        compressed = zstd.compress(raw_content)
        if not isinstance(compressed, bytes):
            compressed = bytes(compressed)
        acep_file = AcepFile.model_construct(content=compressed)
        content = json.dumps(
            acep_file.model_dump(mode="json", by_alias=True),
            separators=(",", ":"),
        ).encode("utf-8")
    else:
        raw_content = cbor2.dumps(src)
        content_size = len(raw_content)
        compressed = zstd.compress(raw_content)
        if not isinstance(compressed, bytes):
            compressed = bytes(compressed)
        compressed_content_size = len(compressed)
        content = Acep2File.build(
            {
                "header": {
                    "header_size": 0,
                    "content_offset": 192,
                    "compressed_content_size": compressed_content_size,
                    "content_size": content_size,
                    "encrypted_metadata": b"\x00" * 138,
                    "content_hash": b"\x00" * 16,
                },
                "compressed_content": compressed,
            }
        )
    target.write_bytes(content)
