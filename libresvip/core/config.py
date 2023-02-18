from confz import ConfZ, ConfZFileSource
from pydantic import Field

from .constants import app_dir


class LibreSvipSettings(ConfZ):
    language: str = Field("简体中文", title="语言", regex="^(简体中文|English)$")
    dark_mode: bool = Field(False, title="暗黑模式")


config_path = app_dir.user_config_path / "settings.yml"


settings = LibreSvipSettings(
    config_sources=ConfZFileSource(file=config_path, optional=True)
)
