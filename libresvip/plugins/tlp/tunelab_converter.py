import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.text import to_unicode

from .model import TuneLabProject
from .options import InputOptions, OutputOptions
from .tunelab_generator import TuneLabGenerator
from .tunelab_parser import TuneLabParser


class TuneLabConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        tlp_project = TuneLabProject.model_validate_json(to_unicode(path.read_bytes()))
        return TuneLabParser(options).parse_project(tlp_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        tlp_project = TuneLabGenerator(options).generate_project(project)
        path.write_bytes(
            json.dumps(
                tlp_project.model_dump(mode="json", by_alias=True),
                ensure_ascii=False,
            ).encode("utf-8")
        )
