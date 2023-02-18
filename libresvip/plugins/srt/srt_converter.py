__package__ = "libresvip.plugins.srt"

import pathlib

from pysrt import SubRipFile

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .srt_generator import SrtGenerator


class SrtConverter(plugin_base.LyricConverterBase):
    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        items = SrtGenerator(options).generate_project(project)
        SubRipFile(items).save(path, encoding=options.encoding)
