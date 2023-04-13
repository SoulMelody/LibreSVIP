__package__ = "libresvip.plugins.ustx"
import pathlib

import yaml

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils import to_unicode

from .model import USTXProject
from .options import InputOptions, OutputOptions
from .ustx_generator import UstxGenerator
from .ustx_parser import UstxParser


class OpenUtauConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        proj_text = to_unicode(path.read_bytes())
        ustx_project = USTXProject.model_validate(yaml.safe_load(proj_text))
        return UstxParser(options).parse_project(ustx_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        ustx_project = UstxGenerator(options).generate_project(project)
        proj_dict = ustx_project.model_dump(by_alias=True)
        proj_text = yaml.safe_dump(proj_dict, allow_unicode=True)
        path.write_text(proj_text)
