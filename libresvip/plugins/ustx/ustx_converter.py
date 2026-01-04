import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.text import to_unicode
from libresvip.utils.yamlutils import dump_yaml_1_2, load_yaml_1_2

from .model import USTXProject
from .options import InputOptions, OutputOptions
from .ustx_generator import UstxGenerator
from .ustx_parser import UstxParser


class OpenUtauConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ustx.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ustx"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        proj_text = to_unicode(path.read_bytes())
        ustx_project = USTXProject.model_validate(load_yaml_1_2(proj_text), context={"path": path})
        return UstxParser(options_obj).parse_project(ustx_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        ustx_project = UstxGenerator(options_obj).generate_project(project)
        proj_dict = ustx_project.model_dump(by_alias=True, exclude_none=True)
        proj_text = dump_yaml_1_2(proj_dict)
        path.write_bytes(proj_text.encode("utf-8"))
