import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocalShifterProjectData
from .options import InputOptions
from .vocalshifter_parser import VocalShifterParser


class VocalShifterConverter(plugin_base.ReadOnlyConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        vshp_proj = VocalShifterProjectData.parse_file(path)
        return VocalShifterParser(options).parse_project(vshp_proj)
