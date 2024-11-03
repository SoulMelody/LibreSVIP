from __future__ import annotations

import contextlib
import contextvars
import dataclasses
import enum
import locale
import pathlib
import re
from typing import TYPE_CHECKING, Optional, cast

from omegaconf import OmegaConf, _utils
from omegaconf.errors import OmegaConfBaseException
from pydantic.dataclasses import dataclass

from .constants import app_dir

if TYPE_CHECKING:
    import yaml

_get_omegaconf_yaml_loader = _utils.get_yaml_loader


def get_omegaconf_yaml_loader() -> yaml.SafeLoader:
    loader = _get_omegaconf_yaml_loader()

    loader.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib._local.Path",
        lambda loader, node: pathlib.Path(*loader.construct_sequence(node)),
    )
    loader.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib._local.PosixPath",
        lambda loader, node: pathlib.PosixPath(*loader.construct_sequence(node)),
    )
    loader.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib._local.WindowsPath",
        lambda loader, node: pathlib.WindowsPath(*loader.construct_sequence(node)),
    )
    return loader


_utils.get_yaml_loader = get_omegaconf_yaml_loader


class LyricsReplaceMode(enum.Enum):
    FULL = "full"
    ALPHABETIC = "alphabetic"
    NON_ALPHABETIC = "non_alphabetic"
    REGEX = "regex"


@dataclass
class LyricsReplacement:
    replacement: str
    pattern_main: str
    pattern_prefix: str = ""
    pattern_suffix: str = ""
    flags: re.RegexFlag = re.IGNORECASE
    mode: LyricsReplaceMode = LyricsReplaceMode.FULL

    def __post_init__(self) -> None:
        if self.mode == LyricsReplaceMode.FULL:
            self.pattern_prefix = "^"
            self.pattern_suffix = "$"
        elif self.mode == LyricsReplaceMode.ALPHABETIC:
            self.pattern_prefix = r"(?<=^|\b)"
            self.pattern_suffix = r"(?=$|\b)"
        elif self.mode == LyricsReplaceMode.NON_ALPHABETIC:
            self.pattern_prefix = self.pattern_suffix = ""
        if self.mode != LyricsReplaceMode.REGEX:
            self.pattern_main = re.escape(self.pattern_main)
        else:
            try:
                self.compiled_pattern
            except re.error as e:
                msg = f"Invalid pattern: {self._pattern}"
                raise ValueError(msg) from e

    @property
    def compiled_pattern(self) -> re.Pattern[str]:
        return re.compile(self._pattern, self.flags)

    @property
    def _pattern(self) -> str:
        return f"{self.pattern_prefix}{self.pattern_main}{self.pattern_suffix}"

    def replace(self, text: str) -> str:
        return self.compiled_pattern.sub(self.replacement, text)


class Language(enum.Enum):
    CHINESE = "zh_CN"
    ENGLISH = "en_US"
    JAPANESE = "ja_JP"

    @staticmethod
    def to_language(locale: str) -> str:
        """Turn a locale name (en_US) into a language name (en-us)."""
        p = locale.find("_")
        if p >= 0:
            return f"{locale[:p].lower()}-{locale[p + 1:].lower()}"
        else:
            return locale.lower()

    @classmethod
    def from_locale(cls, locale: str) -> Language:
        locale = cls.to_language(locale)
        if locale == "zh-cn":
            return cls.CHINESE
        elif locale == "ja-jp":
            return cls.JAPANESE
        else:
            return cls.ENGLISH

    @classmethod
    def auto(cls) -> Language:
        sys_locale = locale.getdefaultlocale()[0]
        return cls.from_locale(sys_locale or "en_US")


class DarkMode(enum.Enum):
    LIGHT = "Light"
    DARK = "Dark"
    SYSTEM = "System"


class ConflictPolicy(enum.Enum):
    SKIP = "Skip"
    OVERWRITE = "Overwrite"
    PROMPT = "Prompt"


class ConversionMode(enum.Enum):
    DIRECT = "Direct"
    SPLIT = "Split"
    MERGE = "Merge"


@dataclass
class LibreSvipBaseUISettings:
    language: Language = dataclasses.field(default_factory=Language.auto)
    last_input_format: Optional[str] = dataclasses.field(default=None)
    last_output_format: Optional[str] = dataclasses.field(default=None)
    dark_mode: DarkMode = dataclasses.field(default=DarkMode.SYSTEM)
    auto_detect_input_format: bool = dataclasses.field(default=True)
    reset_tasks_on_input_change: bool = dataclasses.field(default=True)
    max_track_count: int = dataclasses.field(default=1)
    lyric_replace_rules: dict[str, list[LyricsReplacement]] = dataclasses.field(
        default_factory=dict
    )


ui_settings_ctx: contextvars.ContextVar[Optional[LibreSvipBaseUISettings]] = contextvars.ContextVar(
    "ui_settings_ctx"
)


@dataclass
class LibreSvipSettings(LibreSvipBaseUISettings):
    disabled_plugins: list[str] = dataclasses.field(default_factory=list)
    # GUI Only
    save_folder: pathlib.Path = dataclasses.field(default=pathlib.Path("./"))
    folder_presets: list[pathlib.Path] = dataclasses.field(default_factory=list)
    conflict_policy: ConflictPolicy = dataclasses.field(default=ConflictPolicy.PROMPT)
    multi_threaded_conversion: bool = dataclasses.field(default=True)
    open_save_folder_on_completion: bool = dataclasses.field(default=True)
    auto_set_output_extension: bool = dataclasses.field(default=True)
    auto_check_for_updates: bool = dataclasses.field(default=True)


config_path = app_dir.user_config_path / "settings.yml"


settings = cast(LibreSvipSettings, OmegaConf.structured(LibreSvipSettings))
settings.lyric_replace_rules.setdefault("default", [])
if config_path.exists():
    with contextlib.suppress(OmegaConfBaseException):
        settings = cast(
            LibreSvipSettings,
            OmegaConf.merge(settings, OmegaConf.load(config_path)),
        )


def get_ui_settings() -> LibreSvipBaseUISettings:
    return ui_settings_ctx.get(None) or settings


def save_settings() -> None:
    app_dir.user_config_path.mkdir(parents=True, exist_ok=True)
    OmegaConf.save(settings, config_path)
