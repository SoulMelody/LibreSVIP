import io
import pathlib
import sys
from importlib.resources import files

try:
    try:
        __import__("Cryptodome")
    except ImportError:
        sys.modules["Cryptodome"] = __import__("Crypto")
    from pyzipper import WZ_AES, ZIP_STORED, AESZipFile

    PYZIPPER_AVAILABLE = True
except ImportError:
    PYZIPPER_AVAILABLE = False

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .model import PocketSingerMetadata
from .options import InputOptions, OutputOptions
from .pocket_singer_generator import PocketSingerGenerator
from .pocket_singer_parser import PocketSingerParser

POCKET_SIGER_PASSWORD = b"a022ab39cb3b7b1de92ee441978c9e08"


class PocketSingerConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ps_project.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ps_project"
    _skipload_ = not PYZIPPER_AVAILABLE
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        with AESZipFile(
            io.BytesIO(path.read_bytes()), "r", compression=ZIP_STORED, encryption=WZ_AES
        ) as archive_file:
            archive_file.setpassword(POCKET_SIGER_PASSWORD)
            metadata = PocketSingerMetadata.model_validate_json(
                archive_file.read("config.json"),
                context={
                    "extract_audio": options_obj.extract_audio,
                    "path": path,
                    "archive_file": archive_file,
                },
            )
            return PocketSingerParser(options_obj, archive_file, path).parse_project(metadata)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        buffer = io.BytesIO()
        if len(project.song_tempo_list) != 1:
            project = reset_time_axis(project, options_obj.tempo)
        with AESZipFile(buffer, "w", compression=ZIP_STORED, encryption=WZ_AES) as archive_file:
            archive_file.setpassword(POCKET_SIGER_PASSWORD)
            generator = PocketSingerGenerator(options_obj)
            metadata = generator.generate_project(project)
            archive_file.writestr(
                "config.json",
                metadata.model_dump_json(exclude_none=True, by_alias=True).encode("utf-8"),
            )
            archive_file.writestr(metadata.ace_file_name, generator.buffer.getvalue())
            for audio_name, audio_path in generator.audio_paths.items():
                archive_file.writestr(audio_name, audio_path.read_bytes())
        path.write_bytes(buffer.getvalue())
