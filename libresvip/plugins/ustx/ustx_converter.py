__package__ = "libresvip.plugins.ustx"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils import to_unicode

from .model import USTXProject
from .options import InputOptions, OutputOptions
from .ustx_generator import UstxGenerator
from .ustx_parser import UstxParser


class OpenUtauConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ustx_project = USTXProject.parse_raw(to_unicode(path.read_bytes()))
        return UstxParser(options).parse_project(ustx_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        ustx_project = UstxGenerator(options).generate_project(project)
        yaml_text = ustx_project.yaml(by_alias=True)
        path.write_text(yaml_text, encoding="utf-8")
