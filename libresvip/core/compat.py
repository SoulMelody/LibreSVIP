import sys

try:
    import ujson as json
except ImportError:
    import json

    if hasattr(json, "_default_encoder"):
        json._default_encoder.item_separator = ","
        json._default_encoder.key_separator = ":"

__all__ = ["Traversable", "ZipFile", "json"]

if sys.version_info < (3, 11):
    from importlib_resources.abc import Traversable
    from repro_zipfile import ReproducibleZipFile as ZipFile
else:
    from importlib.resources.abc import Traversable
    from zipfile import ZipFile
