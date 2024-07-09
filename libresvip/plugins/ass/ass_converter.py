import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .ass_generator import AssGenerator
from .options import OutputOptions


class AssConverter(plugin_base.WriteOnlyConverterBase):
    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ssa_obj = AssGenerator(options).generate_project(project)
        path.write_bytes(ssa_obj.to_string("ass").encode(options.encoding))
