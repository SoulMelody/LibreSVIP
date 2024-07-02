import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .ace_studio_generator import AceGenerator
from .ace_studio_parser import AceParser
from .acep_io import compress_ace_studio_project, decompress_ace_studio_project
from .model import AcepProject
from .options import InputOptions, OutputOptions


class ACEStudioConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        obj = decompress_ace_studio_project(path)
        acep_project = AcepProject.model_validate(obj, context={"path": path})
        return AceParser(options=options).parse_project(acep_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ace_project = AceGenerator(options=options).generate_project(project)
        compress_ace_studio_project(ace_project.model_dump(mode="json", by_alias=True), path)
