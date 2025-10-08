import io
import pathlib
from importlib.resources import files

from libresvip.core.compat import ZipFile, json
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
        with ZipFile(io.BytesIO(path.read_bytes()), "r") as archive_file:
            proj = VocaloidProject.model_validate_json(
                archive_file.read("Project/sequence.json").decode("utf-8"),
                context={
                    "extract_audio": options_obj.extract_audio,
                    "path": path,
                    "archive_file": archive_file,
                },
            )
            return VocaloidParser(options_obj, path).parse_project(proj)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        buffer = io.BytesIO()
        generator = VocaloidGenerator(options_obj)
        vocaloid_project = generator.generate_project(project)
        with ZipFile(buffer, "w") as archive_file:
            archive_file.writestr(
                "Project/sequence.json",
                json.dumps(
                    vocaloid_project.model_dump(mode="json", exclude_none=True, by_alias=True),
                    ensure_ascii=False,
                ),
            )
            for wav_name, wav_path in generator.wav_paths.items():
                archive_file.writestr(f"Project/Audio/{wav_name}", wav_path.read_bytes())
        path.write_bytes(buffer.getvalue())
