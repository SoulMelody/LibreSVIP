import io
import pathlib
import zipfile

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocaloidProject
from .options import InputOptions, OutputOptions
from .vpr_generator import VocaloidGenerator
from .vpr_parser import VocaloidParser


class VocaloidConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with zipfile.ZipFile(io.BytesIO(path.read_bytes()), "r") as archive_file:
            proj = VocaloidProject.model_validate_json(
                archive_file.read("Project/sequence.json"),
                context={
                    "extract_audio": options.extract_audio,
                    "path": path,
                    "archive_file": archive_file,
                },
            )
            return VocaloidParser(options, path).parse_project(proj)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        buffer = io.BytesIO()
        generator = VocaloidGenerator(options)
        vocaloid_project = generator.generate_project(project)
        with zipfile.ZipFile(buffer, "w") as archive_file:
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
