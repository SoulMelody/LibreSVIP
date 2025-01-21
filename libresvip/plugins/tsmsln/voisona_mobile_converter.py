import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VoiSonaMobileProject, model_to_value_tree
from .options import InputOptions, OutputOptions
from .value_tree import JUCENode, build_tree_dict
from .voisona_mobile_generator import VoiSonaMobileGenerator
from .voisona_mobile_parser import VoiSonaMobileParser


class VoiSonaMobileConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        value_tree = JUCENode.parse(path.read_bytes())
        tree_dict = build_tree_dict(value_tree)
        tsmsln_project = VoiSonaMobileProject.model_validate(tree_dict["MobileSongEditor"])
        return VoiSonaMobileParser(options).parse_project(tsmsln_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        tsmsln_project = VoiSonaMobileGenerator(options).generate_project(project)
        value_tree = model_to_value_tree(tsmsln_project, name="MobileSongEditor")
        path.write_bytes(JUCENode.build(value_tree))
