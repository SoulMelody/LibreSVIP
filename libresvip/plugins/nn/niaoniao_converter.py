__package__ = "libresvip.plugins.nn"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import NNModel
from .niaoniao_parser import NiaoNiaoParser
from .options import InputOptions, OutputOptions


class NiaoNiaoConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        nn_project = NNModel.model_from_file(path)
        return NiaoNiaoParser(options).parse_project(nn_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        pass
