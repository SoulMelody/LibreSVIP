import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils import to_unicode

from .model import NNModel
from .niaoniao_generator import NiaoniaoGenerator
from .niaoniao_parser import NiaoNiaoParser
from .options import InputOptions, OutputOptions
from .template import render_nn


class NiaoNiaoConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        nn_project = NNModel.model_from_str(to_unicode(path.read_bytes()))
        return NiaoNiaoParser(options).parse_project(nn_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        nn_project = NiaoniaoGenerator(options).generate_project(project)
        render_nn(nn_project, path)
