import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .srt_generator import SrtGenerator


class SrtConverter(plugin_base.WriteOnlyConverterBase):
    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ssa_obj = SrtGenerator(options).generate_project(project)
        path.write_bytes(ssa_obj.to_string("srt").encode(options.encoding))
