import pathlib
from typing import TYPE_CHECKING

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .svg_generator import SvgGenerator

if TYPE_CHECKING:
    from drawsvg import Drawing


class SvgConverter(plugin_base.WriteOnlyConverterBase):
    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        drawing: Drawing = SvgGenerator(options).generate_project(project)
        path.write_bytes(drawing.as_svg().encode("utf-8"))
