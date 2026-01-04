import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import S5pProject
from .options import InputOptions, OutputOptions
from .synthv_editor_generator import SynthVEditorGenerator
from .synthv_editor_parser import SynthVEditorParser


class SynthVEditorConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "s5p.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "s5p"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        s5p_project = S5pProject.model_validate_json(
            path.read_bytes().decode("utf-8"), context={"path": path}
        )
        return SynthVEditorParser(options_obj).parse_project(s5p_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        s5p_project = SynthVEditorGenerator(options_obj).generate_project(project)
        path.write_bytes(
            json.dumps(
                s5p_project.model_dump(mode="json", by_alias=True, exclude_none=True),
                separators=(",", ":"),
            ).encode("utf-8"),
        )
