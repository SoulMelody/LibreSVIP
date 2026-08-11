import pathlib
from importlib.resources import files

from pydantic_core import from_json

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .ace_generator import AceMobileGenerator
from .ace_parser import AceMobileParser
from .model import AceProject
from .options import InputOptions, OutputOptions


class AceMobileConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ace-mobile.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ace"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        content = path.read_bytes()
        try:
            raw_project = from_json(content)
        except ValueError as error:
            if "trailing characters" not in str(error):
                raise
            raw_project = from_json(content, allow_partial=True)
        ace_project = AceProject.model_validate(raw_project)
        return AceMobileParser(options_obj, path).parse_project(ace_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        ace_project = AceMobileGenerator(options_obj).generate_project(project)
        dump_kwargs = {"indent": 2} if options_obj.indented else {"separators": (",", ":")}
        path.write_text(
            json.dumps(
                ace_project.model_dump(mode="json", by_alias=True, exclude_none=True),
                ensure_ascii=False,
                **dump_kwargs,
            ),
            encoding="utf-8",
        )
