import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .lrc_generator import LrcGenerator
from .options import OutputOptions
from .template import render_lrc


class LrcConverter(plugin_base.WriteOnlyConverterBase):
    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        lrc_model = LrcGenerator(options).generate_project(project)
        render_lrc(lrc_model, path)
