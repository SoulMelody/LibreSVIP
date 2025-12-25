import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .aisingers_generator import AiSingersGenerator
from .aisingers_parser import AiSingersParser
from .model import AISProjectBody, AISProjectHead
from .options import InputOptions, OutputOptions


class AiSingersConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "aisp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "aisp"
    _version_ = "1.3.9"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        content = path.read_bytes().decode("utf-8")
        head, _, body = content.partition("\n")
        ais_project_head = AISProjectHead.model_validate_json(head.strip())
        ais_project_body = AISProjectBody.model_validate_json(body.strip())
        return AiSingersParser(options_obj).parse_project(ais_project_head, ais_project_body)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        ais_project_head, ais_project_body = AiSingersGenerator(options_obj).generate_project(
            project
        )
        path.write_bytes(
            (
                json.dumps(
                    ais_project_head.model_dump(mode="json", by_alias=True),
                    separators=(", ", ": "),
                )
                + "\n"
                + json.dumps(
                    ais_project_body.model_dump(mode="json", by_alias=True),
                    separators=(", ", ": "),
                )
            ).encode("utf-8")
        )
