import dataclasses
import enum
import pathlib

from omegaconf import OmegaConf

from .constants import app_dir


class Language(enum.Enum):
    CHINESE = "简体中文"
    ENGLISH = "English"
    JAPANESE = "日本語"

    @classmethod
    def from_locale(cls, locale):
        locale = locale.replace("-", "_").lower()
        if locale == "zh_cn":
            return cls.CHINESE
        elif locale == "ja_jp":
            return cls.JAPANESE
        else:
            return cls.ENGLISH

    def to_locale(self):
        if self == self.CHINESE:
            return "zh_CN"
        elif self == self.JAPANESE:
            return "ja_JP"
        else:
            return "en_US"


class DarkMode(enum.Enum):
    LIGHT = "Light"
    DARK = "Dark"
    SYSTEM = "System"


class ConflictPolicy(enum.Enum):
    SKIP = "Skip"
    OVERWRITE = "Overwrite"
    PROMPT = "Prompt"


@dataclasses.dataclass
class LibreSvipSettings:
    # Common
    language: Language = dataclasses.field(default=Language.CHINESE)
    dark_mode: DarkMode = dataclasses.field(default=DarkMode.SYSTEM)
    # GUI Only
    save_folder: pathlib.Path = dataclasses.field(default=pathlib.Path("./"))
    conflict_policy: ConflictPolicy = dataclasses.field(default=ConflictPolicy.PROMPT)
    auto_detect_input_format: bool = dataclasses.field(default=True)
    auto_set_output_extension: bool = dataclasses.field(default=True)
    reset_tasks_on_input_change: bool = dataclasses.field(default=True)
    multi_threaded_conversion: bool = dataclasses.field(default=True)
    open_save_folder_on_completion: bool = dataclasses.field(default=True)


config_path = app_dir.user_config_path / "settings.yml"


settings = OmegaConf.structured(LibreSvipSettings)
if config_path.exists():
    settings = OmegaConf.merge(settings, OmegaConf.load(config_path))


def save_settings():
    app_dir.user_config_path.mkdir(parents=True, exist_ok=True)
    OmegaConf.save(settings, config_path)
