import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .gjgj_generator import GjgjGenerator
from .gjgj_parser import GjgjParser
from .model import GjgjProject
from .options import InputOptions, OutputOptions


class GjgjConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "gjgj.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "gjgj"
    _version_ = "1.7.3"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        gjgj_project = GjgjProject.model_validate_json(path.read_bytes().decode("utf-8-sig"))
        return GjgjParser(options_obj).parse_project(gjgj_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        gjgj_project = GjgjGenerator(options_obj).generate_project(project)
        path.write_bytes(
            json.dumps(
                gjgj_project.model_dump(
                    mode="json",
                    exclude_none=True,
                    by_alias=True,
                ),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8-sig")
        )
