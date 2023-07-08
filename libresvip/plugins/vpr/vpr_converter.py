import pathlib
import zipfile

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocaloidProject
from .options import InputOptions, OutputOptions

# from .vpr_generator import VocaloidGenerator
from .vpr_parser import VocaloidParser


class VocaloidConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        archive_file = zipfile.ZipFile(path, "r")
        proj = VocaloidProject.model_validate_json(
            archive_file.read("Project/sequence.json")
        )
        return VocaloidParser(options).parse_project(proj)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions):
        return super().dump(path, project, options)
