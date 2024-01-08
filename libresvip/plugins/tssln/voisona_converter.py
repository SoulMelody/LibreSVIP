import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VoiSonaProject, model_to_value_tree
from .options import InputOptions, OutputOptions
from .value_tree import JUCENode, build_tree_dict
from .voisona_generator import VoisonaGenerator
from .voisona_parser import VoiSonaParser


class VoisonaConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        value_tree = JUCENode.parse(path.read_bytes())
        tree_dict = build_tree_dict(value_tree)
        tssln_project = VoiSonaProject.model_validate(tree_dict["TSSolution"])
        return VoiSonaParser(options).parse_project(tssln_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        tssln_project = VoisonaGenerator(options).generate_project(project)
        value_tree = model_to_value_tree(tssln_project)
        path.write_bytes(JUCENode.build(value_tree))
