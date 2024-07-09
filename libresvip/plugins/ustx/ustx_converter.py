import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.text import to_unicode
from libresvip.utils.yamlutils import dump_yaml_1_2, load_yaml_1_2

from .model import USTXProject
from .options import InputOptions, OutputOptions
from .ustx_generator import UstxGenerator
from .ustx_parser import UstxParser


class OpenUtauConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        proj_text = to_unicode(path.read_bytes())
        ustx_project = USTXProject.model_validate(load_yaml_1_2(proj_text), context={"path": path})
        return UstxParser(options).parse_project(ustx_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ustx_project = UstxGenerator(options).generate_project(project)
        proj_dict = ustx_project.model_dump(by_alias=True, exclude_none=True)
        proj_text = dump_yaml_1_2(proj_dict)
        path.write_bytes(proj_text.encode("utf-8"))
