__package__ = "libresvip.plugins.mtp"

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import InputOptions, OutputOptions


class MutaConverter(plugin_base.SVSConverterBase):
    def load(self, path: str, options: InputOptions) -> Project:
        raise NotImplementedError

    def dump(self, path: str, project: Project, options: OutputOptions) -> None:
        raise NotImplementedError
