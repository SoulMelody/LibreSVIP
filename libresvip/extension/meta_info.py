from __future__ import annotations

import contextlib
import dataclasses
from configparser import RawConfigParser
from typing import TYPE_CHECKING, Optional

from loguru import logger
from packaging.specifiers import SpecifierSet
from packaging.version import Version

if TYPE_CHECKING:
    from pathlib import Path


@dataclasses.dataclass
class PluginInfo:
    _config: dataclasses.InitVar[RawConfigParser]
    plugin_object: Optional[object] = None
    name: str = dataclasses.field(init=False)
    module: str = dataclasses.field(init=False)
    version: Version = dataclasses.field(init=False)
    author: str = dataclasses.field(init=False)
    description: str = dataclasses.field(init=False)
    website: str = dataclasses.field(init=False)
    copy_right: str = dataclasses.field(init=False)

    def __post_init__(self, _config: RawConfigParser) -> None:
        self.module = _config.get("Core", "Module")
        self.name = _config.get("Core", "Name")
        self.version = Version(_config.get("Documentation", "Version", fallback="0.0.0"))
        self.author = _config.get("Documentation", "Author", fallback="Unknown Author")
        self.description = (
            _config.get("Documentation", "Description", fallback="")
            .encode("raw_unicode_escape")
            .decode("unicode_escape")
        )
        self.website = _config.get("Documentation", "Website", fallback="")
        self.copy_right = _config.get("Documentation", "Copyright", fallback="Unknown")

    @classmethod
    def load(cls, plugfile_path: Path) -> Optional[PluginInfo]:
        try:
            with plugfile_path.open(encoding="utf-8") as metafile:
                cp = RawConfigParser()
                cp.read_file(metafile)
                return cls(cp)
        except Exception:
            logger.exception(f"Failed to load plugin info from {plugfile_path}")

    @classmethod
    def load_from_string(cls, content: str) -> Optional[PluginInfo]:
        with contextlib.suppress(Exception):
            cp = RawConfigParser()
            cp.read_string(content)
            return cls(cp)


@dataclasses.dataclass
class LibreSvipPluginInfo(PluginInfo):
    file_format: str = dataclasses.field(init=False)
    suffix: str = dataclasses.field(init=False)
    target_framework: SpecifierSet = dataclasses.field(init=False)
    icon_base64: Optional[str] = dataclasses.field(init=False)

    def __post_init__(self, _config: RawConfigParser) -> None:
        super().__post_init__(_config)
        self.file_format = _config.get("Documentation", "Format")
        self.suffix = _config.get("Documentation", "Suffix")
        self.target_framework = SpecifierSet(
            _config.get("Documentation", "TargetFramework", fallback=">=0.0.0")
        )
        self.icon_base64 = _config.get("Documentation", "IconBase64", fallback=None)
