import contextlib
import sys

try:
    import ujson as json
except ImportError:
    import json

    if hasattr(json, "_default_encoder"):
        json._default_encoder.item_separator = ","
        json._default_encoder.key_separator = ":"

with contextlib.suppress(ImportError):
    sys.modules["yaml"] = __import__("yaml_ft")

__all__ = ["Traversable", "json"]

if sys.version_info < (3, 11):
    from importlib_resources.abc import Traversable
else:
    from importlib.resources.abc import Traversable
