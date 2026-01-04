import io
import pathlib
from importlib.resources import files

from upath import UPath

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .model import VOXFactoryProject
from .options import InputOptions, OutputOptions
from .vox_factory_generator import VOXFactoryGenerator
from .vox_factory_parser import VOXFactoryParser


class VOXFactoryConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vfp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vfp"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        zip_path = UPath("zip://", fo=io.BytesIO(path.read_bytes()), mode="r")
        proj = VOXFactoryProject.model_validate_json(
            (zip_path / "project.json").read_bytes(),
            context={
                "extract_audio": options_obj.extract_audio,
                "path": path,
                "archive_file": zip_path,
            },
        )
        return VOXFactoryParser(options_obj, path).parse_project(proj)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        if len(project.song_tempo_list) != 1:
            project = reset_time_axis(project, options_obj.tempo)
        buffer = io.BytesIO()
        generator = VOXFactoryGenerator(options_obj)
        vox_factory_project = generator.generate_project(project)
        zip_path = UPath("zip://", fo=buffer, mode="a")
        (zip_path / "project.json").write_text(
            json.dumps(
                vox_factory_project.model_dump(mode="json", by_alias=True),
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (zip_path / "resources").mkdir()
        for audio_name, audio_path in generator.audio_paths.items():
            (zip_path / f"resources/{audio_name}").write_bytes(audio_path.read_bytes())
        path.write_bytes(buffer.getvalue())
