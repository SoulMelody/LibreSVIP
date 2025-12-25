import pathlib
from importlib.resources import files
from typing import Any

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.base import Project as OpenSvipProject

from .options import InputOptions, OutputOptions


class JsonSvipConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "jsonsvip.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "json"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        return OpenSvipProject.model_validate_json(path.read_bytes().decode("utf-8"))

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        dump_kwargs: dict[str, Any] = (
            {"indent": 2} if options_obj.indented else {"separators": (",", ":")}
        )
        path.write_bytes(
            json.dumps(
                project.model_dump(mode="json", by_alias=True),
                ensure_ascii=False,
                **dump_kwargs,
            ).encode("utf-8"),
        )
