__package__ = "libresvip.plugins.dv"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import InputOptions, OutputOptions


class DeepVocalConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        raise NotImplementedError

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        raise NotImplementedError
