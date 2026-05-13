import io
import pathlib
import zipfile
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .ace_studio_generator import AceGenerator
from .ace_studio_parser import AceParser
from .acep_io import ZSTD_AVAILABLE, compress_ace_studio_project, decompress_ace_studio_project
from .model import AcepProject
from .options import InputOptions, OutputOptions


class ACEStudioConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ace-studio.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "acep"
    _skipload_ = not ZSTD_AVAILABLE
    _version_ = "2.0.7"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        if path.suffix == ".acet":
            zip_path = zipfile.Path(io.BytesIO(path.read_bytes()))
            for item in zip_path.iterdir():
                if item.name.endswith(".acep"):
                    path = item
                    break
        obj = decompress_ace_studio_project(path)
        acep_project = AcepProject.model_validate(obj, context={"path": path})
        return AceParser(options=cls.input_option_cls.model_validate(options)).parse_project(
            acep_project
        )

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        ace_project = AceGenerator(options=options_obj).generate_project(project)
        compress_ace_studio_project(
            ace_project.model_dump(mode="json", by_alias=True), path, options_obj.serialization
        )
