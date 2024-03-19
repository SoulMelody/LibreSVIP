# This submodule is adapted from https://github.com/kislyuk/yq/.
from typing import Any

try:
    import io

    from ruamel.yaml import YAML

    def load_yaml_1_2(text: str) -> dict[str, Any]:
        with YAML(typ="safe") as yml:
            return yml.load(text)

    def dump_yaml_1_2(data: dict[str, Any]) -> str:
        stream = io.StringIO()
        with YAML(typ="rtsc", output=stream) as yml:
            yml.dump(data)
            return stream.getvalue()

except ImportError:
    import yaml

    from .dumper import get_dumper
    from .loader import get_loader

    def load_yaml_1_2(text: str) -> dict[str, Any]:
        return yaml.load(text, get_loader())

    def dump_yaml_1_2(data: dict[str, Any]) -> str:
        return yaml.dump(
            data,
            None,
            get_dumper(grammar_version="1.2"),
            allow_unicode=True,
            sort_keys=False,
        )
