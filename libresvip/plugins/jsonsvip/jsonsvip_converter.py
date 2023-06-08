__package__ = "libresvip.plugins.jsonsvip"

import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.base import Project as OpenSvipProject

from .options import InputOptions, OutputOptions


class JsonSvipConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        return OpenSvipProject.parse_file(path)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        if options is None:
            options = OutputOptions()
        dump_kwargs = {"encoding": "utf-8"}
        if options.indented:
            dump_kwargs["indent"] = 2
        else:
            dump_kwargs["separators"] = (",", ":")
        path.write_text(project.json(by_alias=True, ensure_ascii=False, **dump_kwargs))
