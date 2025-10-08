import contextlib
import hashlib
import importlib
import pathlib
import sys
from typing import Any

from pydantic import Base64Bytes, Field, ValidationInfo, field_validator

from libresvip.core.compat import json
from libresvip.core.exceptions import UnsupportedProjectVersionError
from libresvip.model.base import BaseModel
from libresvip.utils.translation import gettext_lazy as _

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
    return unpad(cipher.decrypt(content), AES.block_size, style="iso7816")


def decrypt_acep_content_v2(content: bytes, salt: str) -> bytes:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad

    iv_bytes = str(int(salt[33:], 16) & 0x49A23B22DD28F042).encode()
    iv = hashlib.md5(iv_bytes).digest()
    key = b"\xb7\x4b\x57\x57\x5f\xb1\x4f\xc7\xec\xa9\x9c\x8b\x82\x53\x10\xfc\x4a\x33\x7b\x83\x7b\x12\x83\xe9\x0e\xe0\xef\x02\x20\x1c\x91\x12"
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(content), AES.block_size, style="iso7816")


def decompress_ace_studio_project(src: pathlib.Path) -> dict[str, Any]:
    acep_file = AcepFile.model_validate_json(src.read_bytes().decode("utf-8"))
    if acep_file.version == 1:
        content = decrypt_acep_content_v1(acep_file.content)
    elif acep_file.version == 2:
        content = decrypt_acep_content_v2(acep_file.content, acep_file.salt)
    else:
        content = acep_file.content
    decompressed = zstd.decompress(content)
    return json.loads(decompressed)


def compress_ace_studio_project(src: dict[str, Any], target: pathlib.Path) -> None:
    raw_content = json.dumps(src).encode()
    compressed = zstd.compress(raw_content)
    acep_file = AcepFile.model_construct(content=compressed)
    target.write_bytes(
        json.dumps(
            acep_file.model_dump(mode="json", by_alias=True),
            separators=(",", ":"),
        ).encode("utf-8")
    )
