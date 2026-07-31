from __future__ import annotations

import contextlib
import importlib
from typing import TYPE_CHECKING, Any

from libresvip.core.compat import json
from libresvip.core.exceptions import InvalidFileTypeError, UnsupportedProjectVersionError
from libresvip.utils.translation import gettext_lazy as _

from .model_v1 import Model

if TYPE_CHECKING:
    from pydantic import BaseModel

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

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


VERSION_MODELS: dict[str, type[BaseModel]] = {
    "1.0.0": Model,
}


def _as_bytes(value: Any) -> bytes:
    return value if isinstance(value, bytes) else bytes(value)


def decompress(data: bytes) -> bytes:
    if data.startswith(ZSTD_MAGIC):
        return _as_bytes(zstd.decompress(data))
    return data


def compress(data: bytes) -> bytes:
    return _as_bytes(zstd.compress(data))


def load_model(data: bytes) -> Model:
    raw_data = json.loads(decompress(data))
    if not isinstance(raw_data, dict):
        msg = _("Invalid DSPX project")
        raise InvalidFileTypeError(msg)
    version = raw_data.get("version")
    if not isinstance(version, str) or version not in VERSION_MODELS:
        msg = _("Unsupported project version") + f": {version!r}"
        raise UnsupportedProjectVersionError(msg)
    model = VERSION_MODELS[version].model_validate(raw_data)
    if not isinstance(model, Model):
        msg = _("Unsupported project version") + f": {version!r}"
        raise UnsupportedProjectVersionError(msg)
    return model


def dump_model(model: Model) -> bytes:
    data = model.model_dump(mode="json", by_alias=True)
    validated = Model.model_validate(data)
    json_data = json.dumps(
        validated.model_dump(mode="json", by_alias=True),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return compress(json_data)
