import io
import pathlib
import zipfile

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VOXFactoryProject
from .options import InputOptions, OutputOptions
from .vox_factory_generator import VOXFactoryGenerator
from .vox_factory_parser import VOXFactoryParser


class VOXFactoryConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with zipfile.ZipFile(io.BytesIO(path.read_bytes()), "r") as archive_file:
            proj = VOXFactoryProject.model_validate_json(
                archive_file.read("project.json"),
                context={
                    "extract_audio": options.extract_audio,
                    "path": path,
                    "archive_file": archive_file,
                },
            )
            return VOXFactoryParser(options, path).parse_project(proj)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        buffer = io.BytesIO()
        generator = VOXFactoryGenerator(options)
        vox_factory_project = generator.generate_project(project)
        with zipfile.ZipFile(buffer, "w") as archive_file:
            archive_file.writestr(
                "project.json",
                json.dumps(
                    vox_factory_project.model_dump(mode="json", exclude_none=True, by_alias=True),
                    ensure_ascii=False,
                ),
            )
            for audio_name, audio_path in generator.audio_paths.items():
                archive_file.writestr(f"resources/{audio_name}", audio_path.read_bytes())
        path.write_bytes(buffer.getvalue())
