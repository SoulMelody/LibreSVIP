import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.text import to_unicode

from .model import UFData
from .options import InputOptions, OutputOptions
from .ufdata_generator import UFDataGenerator
from .ufdata_parser import UFDataParser


class UFDataConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ufdata_project = UFData.model_validate_json(to_unicode(path.read_bytes()))
        return UFDataParser(options).parse_project(ufdata_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ufdata_project = UFDataGenerator(options).generate_project(project)
        path.write_bytes(
            json.dumps(
                ufdata_project.model_dump(mode="json", by_alias=True),
                ensure_ascii=False,
            ).encode("utf-8")
        )
