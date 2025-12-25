import io
import pathlib
from importlib.resources import files

from upath import UPath

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocaloidProject
from .options import InputOptions, OutputOptions
from .vpr_generator import VocaloidGenerator
from .vpr_parser import VocaloidParser


class VocaloidConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vpr.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vpr"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        zip_path = UPath("zip://", fo=io.BytesIO(path.read_bytes()), mode="r")
        proj = VocaloidProject.model_validate_json(
            (zip_path / "Project/sequence.json").read_bytes(),
            context={
                "extract_audio": options_obj.extract_audio,
                "path": path,
                "archive_file": zip_path,
            },
        )
        return VocaloidParser(options_obj, path).parse_project(proj)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        buffer = io.BytesIO()
        generator = VocaloidGenerator(options_obj)
        vocaloid_project = generator.generate_project(project)
        zip_path = UPath("zip://", fo=buffer, mode="a")
        (zip_path / "Project/sequence.json").write_text(
            json.dumps(
                vocaloid_project.model_dump(mode="json", exclude_none=True, by_alias=True),
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        for wav_name, wav_path in generator.wav_paths.items():
            (zip_path / f"Project/Audio/{wav_name}").write_bytes(wav_path.read_bytes())
        path.write_bytes(buffer.getvalue())
