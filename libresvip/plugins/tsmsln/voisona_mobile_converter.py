import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.binary.value_tree import JUCENode, build_tree_dict

from .model import VoiSonaMobileProject, model_to_value_tree
from .options import InputOptions, OutputOptions
from .voisona_mobile_generator import VoiSonaMobileGenerator
from .voisona_mobile_parser import VoiSonaMobileParser


class VoiSonaMobileConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "tsmsln.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "tsmsln"
    _version_ = "1.12.1"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        value_tree = JUCENode.parse(path.read_bytes())
        tree_dict = build_tree_dict(value_tree)
        tsmsln_project = VoiSonaMobileProject.model_validate(tree_dict["MobileSongEditor"])
        return VoiSonaMobileParser(options_obj).parse_project(tsmsln_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        tsmsln_project = VoiSonaMobileGenerator(options_obj).generate_project(project)
        value_tree = model_to_value_tree(tsmsln_project, name="MobileSongEditor")
        path.write_bytes(JUCENode.build(value_tree))
