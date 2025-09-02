import pathlib

import ms3

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .mscz_parser import MsczParser
from .options import InputOptions


class MsczConverter(plugin_base.ReadOnlyConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        score = ms3.Score(path)
        return MsczParser().parse_project(score)
