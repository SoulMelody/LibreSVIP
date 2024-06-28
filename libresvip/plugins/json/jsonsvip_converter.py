import pathlib
from typing import Any

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.base import Project as OpenSvipProject

from .options import InputOptions, OutputOptions


class JsonSvipConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        return OpenSvipProject.model_validate_json(path.read_bytes().decode("utf-8"))

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        dump_kwargs: dict[str, Any] = (
            {"indent": 2} if options.indented else {"separators": (",", ":")}
        )
        path.write_bytes(
            json.dumps(
                project.model_dump(mode="json", by_alias=True),
                ensure_ascii=False,
                **dump_kwargs,
            ).encode("utf-8"),
        )
