import dataclasses

from libresvip.model.base import Project

from .model import VxFile
from .options import OutputOptions


@dataclasses.dataclass
class VxBetaGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> VxFile:
        return VxFile()
