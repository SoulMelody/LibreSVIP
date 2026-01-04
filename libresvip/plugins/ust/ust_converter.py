import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import UstWalker, get_ust_grammar
from .options import InputOptions, OutputOptions
from .template import render_ust
from .ust_generator import USTGenerator
from .ust_parser import USTParser


class USTConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ust.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ust"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        ust_content = path.read_bytes()
        ust_text = ust_content.decode(options_obj.encoding, errors="replace")
        tree = get_ust_grammar().parse(ust_text)
        ust_project = UstWalker().walk(tree)
        return USTParser(options_obj).parse_project(ust_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        ust_project = USTGenerator(options_obj).generate_project(project)
        render_ust(ust_project, path, options_obj.encoding)
