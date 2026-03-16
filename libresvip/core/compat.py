import contextlib
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

try:
    from minijinja import Environment as JinjaEnvironment
except ImportError:
    from jinja2 import Template

    class JinjaEnvironment:
        def __init__(self) -> None:
            self._compiled_templates: dict[str, Template] = {}

        def add_template(self, name: str, source: str) -> None:
            self._compiled_templates[name] = Template(source)

        def render_template(self, template_name: str, **ctx: dict[str, Any]) -> str:
            return self._compiled_templates[template_name].render(**ctx)


jinja_env = JinjaEnvironment()

__all__ = ["Traversable", "jinja_env", "json"]

if sys.version_info < (3, 11):
    from importlib_resources.abc import Traversable
else:
    from importlib.resources.abc import Traversable
