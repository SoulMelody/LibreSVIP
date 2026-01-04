import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.binary.value_tree import JUCENode, build_tree_dict

from .model import VoiSonaProject, model_to_value_tree
from .options import InputOptions, OutputOptions
from .voisona_generator import VoiSonaGenerator
from .voisona_parser import VoiSonaParser


class VoiSonaConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "tssln.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "tssln"
    _version_ = "1.12.1"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        value_tree = JUCENode.parse(path.read_bytes())
        tree_dict = build_tree_dict(value_tree)
        tssln_project = VoiSonaProject.model_validate(tree_dict["TSSolution"])
        return VoiSonaParser(options_obj).parse_project(tssln_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        tssln_project = VoiSonaGenerator(options_obj).generate_project(project)
        value_tree = model_to_value_tree(tssln_project)
        path.write_bytes(JUCENode.build(value_tree))
