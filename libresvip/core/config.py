import dataclasses
import enum

from omegaconf import OmegaConf

from .constants import app_dir


class Language(enum.Enum):
    CHINESE = "简体中文"
    ENGLISH = "English"


@dataclasses.dataclass
class LibreSvipSettings:
    language: Language = dataclasses.field(default=Language.CHINESE)
    dark_mode: bool = dataclasses.field(default=False)


config_path = app_dir.user_config_path / "settings.yml"


settings = OmegaConf.structured(LibreSvipSettings)
if config_path.exists():
    settings = OmegaConf.merge(
        settings, OmegaConf.load(config_path)
    )
