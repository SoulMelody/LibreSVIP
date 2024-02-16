import pathlib

from srt import compose

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .srt_generator import SrtGenerator


class SrtConverter(plugin_base.WriteOnlyConverterBase):
    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        items = SrtGenerator(options).generate_project(project)
        path.write_bytes(compose(items).encode(options.encoding))
