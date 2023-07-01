__package__ = "libresvip.plugins.svg"

import pathlib

from drawsvg import Drawing

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .svg_generator import SvgGenerator


class SvgConverter(plugin_base.WriteOnlyConverterBase):
    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        drawing: Drawing = SvgGenerator(options).generate_project(project)
        drawing.save_svg(path)
