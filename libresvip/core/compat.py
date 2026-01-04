import contextlib
import inspect
import sys
from typing import Any

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

import xsdata
from packaging.version import Version

if Version(xsdata.__version__) <= Version("25.7"):
    from xsdata.exceptions import XmlContextError
    from xsdata.formats.dataclass.models.builders import XmlMetaBuilder

    def find_declared_class(cls: XmlMetaBuilder, clazz: type, name: str) -> Any:
        for base in clazz.__mro__:
            ann = inspect.get_annotations(base)
            if ann and name in ann:
                return base

        msg = f"Failed to detect the declared class for field {name}"
        raise XmlContextError(msg)

    XmlMetaBuilder.find_declared_class = classmethod(find_declared_class)
