from __future__ import annotations

import contextvars
import enum
import locale
import pathlib
import re
from typing import Annotated, Any, Optional, TypeVar, Union

import pydantic_settings
import yaml
from pydantic import BaseModel, Field, GetCoreSchemaHandler, ValidationError
from pydantic_core import core_schema

try:
    from yaml import CSafeLoader as DefaultSafeLoader
except ImportError:
    from yaml import SafeLoader as DefaultSafeLoader

from libresvip.core.constants import app_dir

T = TypeVar("T", bound="YamlSettings")
E = TypeVar("E", bound=enum.Enum)
YAML_BOOL_TYPES = [
    "y",
    "Y",
    "yes",
    "Yes",
    "YES",
    "n",
    "N",
    "no",
    "No",
    "NO",
    "true",
    "True",
    "TRUE",
    "false",
    "False",
    "FALSE",
    "on",
    "On",
    "ON",
    "off",
    "Off",
    "OFF",
]


def pydantic_enum(enum_cls: type[E]) -> type[E]:
    def _get_pydantic_core_schema_(
        cls: type[E], source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.WrapValidatorFunctionSchema:
        assert source_type is cls

        def get_enum(value: Any, validate_next: core_schema.ValidatorFunctionWrapHandler) -> E:
            if isinstance(value, cls):
                return value
            else:
                name: str = validate_next(value)
                return enum_cls[name]

        def serialize(enum: E) -> str:
            return enum.name

        expected = [member.name for member in cls]
        name_schema = core_schema.literal_schema(expected)

        return core_schema.no_info_wrap_validator_function(
            get_enum,
            name_schema,
            ref=cls.__name__,
            serialization=core_schema.plain_serializer_function_ser_schema(serialize),
        )

    setattr(enum_cls, "__get_pydantic_core_schema__", classmethod(_get_pydantic_core_schema_))
    return enum_cls


def get_omega_conf_loader() -> DefaultSafeLoader:
    class OmegaConfLoader(DefaultSafeLoader):
        def construct_mapping(self, node: yaml.Node, deep: bool = False) -> Any:
            keys = set()
            for key_node, _ in node.value:
                if key_node.tag != yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG:
                    continue
                if key_node.value in keys:
                    msg = "while constructing a mapping"
                    raise yaml.constructor.ConstructorError(
                        msg,
                        node.start_mark,
                        f"found duplicate key {key_node.value}",
                        key_node.start_mark,
                    )
                keys.add(key_node.value)
            return super().construct_mapping(node, deep=deep)

    loader_class = OmegaConfLoader
    loader_class.add_implicit_resolver(
        "tag:yaml.org,2002:float",
        re.compile(
            """^(?:
         [-+]?[0-9]+(?:_[0-9]+)*\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?[0-9]+(?:_[0-9]+)*(?:[eE][-+]?[0-9]+)
        |\\.[0-9]+(?:_[0-9]+)*(?:[eE][-+][0-9]+)?
        |[-+]?[0-9]+(?:_[0-9]+)*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$""",
            re.X,
        ),
        list("-+0123456789."),
    )
    loader_class.yaml_implicit_resolvers = {
        key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
        for key, resolvers in loader_class.yaml_implicit_resolvers.items()
    }

    loader_class.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib.Path",
        lambda loader, node: pathlib.Path(*loader.construct_sequence(node)),
    )
    loader_class.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib.PosixPath",
        lambda loader, node: pathlib.PosixPath(*loader.construct_sequence(node)),
    )
    loader_class.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib.WindowsPath",
        lambda loader, node: pathlib.WindowsPath(*loader.construct_sequence(node)),
    )
    loader_class.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib._local.Path",
        lambda loader, node: pathlib.Path(*loader.construct_sequence(node)),
    )
    loader_class.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib._local.PosixPath",
        lambda loader, node: pathlib.PosixPath(*loader.construct_sequence(node)),
    )
    loader_class.add_constructor(
        "tag:yaml.org,2002:python/object/apply:pathlib._local.WindowsPath",
        lambda loader, node: pathlib.WindowsPath(*loader.construct_sequence(node)),
    )
    return loader_class


def yaml_is_bool(st: str) -> bool:
    return st in YAML_BOOL_TYPES


def is_float(st: str) -> bool:
    try:
        float(st)
    except ValueError:
        return False
    else:
        return True


def is_int(st: str) -> bool:
    try:
        int(st)
    except ValueError:
        return False
    else:
        return True


class OmegaConfDumper(yaml.Dumper):
    str_representer_added = False

    @staticmethod
    def str_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
        with_quotes = yaml_is_bool(data) or is_int(data) or is_float(data)
        return dumper.represent_scalar(
            yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG,
            data,
            style=("'" if with_quotes else None),
        )


def get_omega_conf_dumper() -> type[OmegaConfDumper]:
    if not OmegaConfDumper.str_representer_added:
        OmegaConfDumper.add_representer(str, OmegaConfDumper.str_representer)
        OmegaConfDumper.str_representer_added = True
    return OmegaConfDumper


class YamlSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(extra="allow", validate_assignment=True)
    _settings_dir: pathlib.Path
    __FILENAME__: str = "settings.yml"

    @classmethod
    def exists(cls, settings_dir: Union[str, pathlib.Path]) -> bool:
        return (pathlib.Path(settings_dir).resolve() / cls.__FILENAME__).exists()

    @classmethod
    def create(cls: type[T], settings_dir: Union[str, pathlib.Path], exists_ok: bool = False) -> T:
        settings_dir = pathlib.Path(settings_dir).resolve()
        if not exists_ok and cls.exists(settings_dir):
            msg = f"`{cls.__FILENAME__}` already exists in `{settings_dir}`"
            raise FileExistsError(msg)
        settings = cls()
        settings._settings_dir = settings_dir
        settings.save()
        return settings

    @classmethod
    def load(
        cls: type[T],
        settings_dir: Union[str, pathlib.Path],
        create_if_missing: bool = False,
        raise_error_if_failed: bool = True,
    ) -> T:
        settings_dir = pathlib.Path(settings_dir).resolve()
        if not cls.exists(settings_dir):
            if create_if_missing:
                return cls.create(settings_dir)
            msg = f"`{cls.__FILENAME__}` not found in `{settings_dir}`"
            raise FileNotFoundError(msg)

        settings_data = yaml.load(
            (settings_dir / cls.__FILENAME__).read_text(encoding="utf-8"), get_omega_conf_loader()
        )
        try:
            settings_object = cls.model_validate(settings_data)
        except ValidationError as e:
            msg = f"Invalid settings data: {e}"
            if raise_error_if_failed:
                raise ValueError(msg)
            settings_object = cls()
        settings_object._settings_dir = settings_dir
        return settings_object

    def save(self) -> None:
        file_path = self._settings_dir / self.__FILENAME__
        try:
            file_path.write_text(
                yaml.dump(self.model_dump(), None, get_omega_conf_dumper()), encoding="utf-8"
            )
        except OSError as e:
            msg = f"Failed to save settings to {file_path}: {e}"
            raise OSError(msg)


class LyricsReplaceMode(enum.Enum):
    FULL = "full"
    ALPHABETIC = "alphabetic"
    NON_ALPHABETIC = "non_alphabetic"
    REGEX = "regex"


class LyricsReplacement(BaseModel):
    replacement: str
    pattern_main: str
    pattern_prefix: str = ""
    pattern_suffix: str = ""
    flags: Annotated[re.RegexFlag, pydantic_enum(re.RegexFlag)] = re.IGNORECASE
    mode: Annotated[LyricsReplaceMode, pydantic_enum(LyricsReplaceMode)] = LyricsReplaceMode.FULL

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
    GERMAN = "de_DE"

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
        return {
            "zh-cn": cls.CHINESE,
            "en-us": cls.ENGLISH,
            "ja-jp": cls.JAPANESE,
            "de-de": cls.GERMAN,
        }[locale]

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


class LibreSvipBaseUISettings(YamlSettings):
    language: Annotated[Language, pydantic_enum(Language)] = Field(default_factory=Language.auto)
    last_input_format: Optional[str] = Field(default=None)
    last_output_format: Optional[str] = Field(default=None)
    dark_mode: Annotated[DarkMode, pydantic_enum(DarkMode)] = Field(default=DarkMode.SYSTEM)
    auto_detect_input_format: bool = Field(default=True)
    reset_tasks_on_input_change: bool = Field(default=True)
    max_track_count: int = Field(default=1)
    lyric_replace_rules: dict[str, list[LyricsReplacement]] = Field(default_factory=dict)


ui_settings_ctx: contextvars.ContextVar[Optional[LibreSvipBaseUISettings]] = contextvars.ContextVar(
    "ui_settings_ctx"
)


class LibreSvipSettings(LibreSvipBaseUISettings):
    disabled_plugins: list[str] = Field(default_factory=list)
    # GUI Only
    save_folder: pathlib.Path = Field(default=pathlib.Path("./"))
    folder_presets: list[pathlib.Path] = Field(default_factory=list)
    conflict_policy: Annotated[ConflictPolicy, pydantic_enum(ConflictPolicy)] = Field(
        default=ConflictPolicy.PROMPT
    )
    multi_threaded_conversion: bool = Field(default=True)
    open_save_folder_on_completion: bool = Field(default=True)
    auto_set_output_extension: bool = Field(default=True)
    auto_check_for_updates: bool = Field(default=True)


config_path = app_dir.user_config_path / "settings.yml"


if config_path.exists():
    settings = LibreSvipSettings.load(
        app_dir.user_config_path, create_if_missing=True, raise_error_if_failed=False
    )
else:
    settings = LibreSvipSettings()
settings.lyric_replace_rules.setdefault("default", [])


def get_ui_settings() -> LibreSvipBaseUISettings:
    return ui_settings_ctx.get(None) or settings


def save_settings() -> None:
    settings.save()
