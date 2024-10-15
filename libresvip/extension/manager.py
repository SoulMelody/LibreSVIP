from __future__ import annotations

import copy
import dataclasses
import functools
import gettext
import inspect
import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import (
    PathFinder,
    SourceFileLoader,
    all_suffixes,
)
from typing import TYPE_CHECKING, Generic, Optional, cast

from loguru import logger
from typing_extensions import TypeGuard

from libresvip.core.compat import package_path
from libresvip.core.config import get_ui_settings, settings
from libresvip.core.constants import app_dir, pkg_dir, res_dir
from libresvip.utils.module_loading import import_module

from .base import BasePlugin_co, MiddlewareBase, SVSConverterBase
from .meta_info import (
    FormatProviderPluginInfo,
    MiddlewarePluginInfo,
    PluginInfo_co,
)

if TYPE_CHECKING:
    import pathlib
    from importlib.machinery import ModuleSpec
    from types import ModuleType

    from libresvip.core.compat import Traversable


@dataclasses.dataclass
class BasePluginManager(Generic[BasePlugin_co, PluginInfo_co]):
    info_extension: str
    plugin_base: type[BasePlugin_co]
    plugin_info_class: type[PluginInfo_co]
    plugin_namespace: str
    install_path: pathlib.Path
    plugin_places: list[Traversable]
    plugin_registry: dict[str, PluginInfo_co] = dataclasses.field(default_factory=dict)
    _candidates: list[tuple[Traversable, PluginInfo_co]] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        sys.meta_path.append(cast(MetaPathFinder, self))

    @functools.cached_property
    def lib_suffixes(self) -> list[str]:
        return all_suffixes()

    def find_spec(
        self,
        fullname: str,
        path: Optional[list[str]],
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        if not fullname.startswith(self.plugin_namespace) or not path:
            return None
        path = [str(path) for path in self.plugin_places]

        if (
            spec := PathFinder.find_spec(fullname, path, target)
        ) is not None and spec.loader is not None:
            spec.loader = SourceFileLoader(spec.loader.name, spec.loader.path)  # type: ignore[attr-defined]
            return spec

    def is_plugin(self, member: object) -> TypeGuard[type[BasePlugin_co]]:
        return (
            inspect.isclass(member)
            and not inspect.isabstract(member)
            and issubclass(member, self.plugin_base)
        )

    def scan_candidates(self) -> None:
        self._candidates.clear()
        _discovered: set[str] = set()
        for dir_path in self.plugin_places:
            # first of all, is it a directory :)
            if not dir_path.is_dir():
                logger.debug(f"{self.__class__.__name__} skips {dir_path} (not a directory)")
                continue
            # iteratively walks through the directory
            for child_path in dir_path.iterdir():
                if not child_path.is_dir():
                    continue
                for file_path in child_path.iterdir():
                    if not file_path.is_file() or not file_path.name.endswith(
                        f".{self.info_extension}"
                    ):
                        continue
                    if (candidate_infofile := str(file_path)) in _discovered:
                        logger.debug(f"{candidate_infofile} rejected because already discovered")
                        continue
                    logger.debug(
                        f"{self.__class__.__name__} found a candidate:\n    {candidate_infofile}"
                    )
                    if (plugin_info := self.plugin_info_class.load(file_path)) is None:
                        logger.debug(f"Plugin candidate '{candidate_infofile}'  rejected")
                        continue  # we consider this was the good strategy to use for: it failed -> not a plugin -> don't try another strategy
                    if entry_suffix := next(
                        (
                            suffix
                            for suffix in self.lib_suffixes
                            if (
                                (
                                    candidate_filepath := (
                                        child_path / f"{plugin_info.module}{suffix}"
                                    )
                                ).is_file()
                            )
                        ),
                        None,
                    ):
                        _discovered.add(
                            str(
                                child_path / f"{plugin_info.module}{entry_suffix}",
                            )
                        )
                    else:
                        logger.error(
                            f"Plugin candidate rejected: cannot find the file or directory module for '{candidate_infofile}'",
                        )
                        break
                    self._candidates.append((candidate_filepath, plugin_info))
                    # finally the candidate_infofile must not be discovered again
                    _discovered.add(candidate_infofile)

    def import_plugins(self, reload: bool = False) -> None:
        if reload:
            self.plugin_registry.clear()
        self.scan_candidates()
        for candidate_filepath, plugin_info in self._candidates:
            # make sure to attribute a unique module name to the one
            # that is about to be loaded
            plugin_module_name = f"{self.plugin_namespace}.{plugin_info.identifier}"
            if (
                plugin_info.identifier in self.plugin_registry and not reload
            ) or plugin_info.identifier in settings.disabled_plugins:
                logger.debug(f"Skipped plugin: {plugin_info.identifier}")
                continue
            try:
                candidate_module = import_module(plugin_module_name, candidate_filepath, reload)
            except Exception as e:
                logger.exception(e)
                logger.error(
                    f"Unable to import plugin: {candidate_filepath}",
                )
                continue

            try:
                plugin_cls_name, plugin_cls = inspect.getmembers(candidate_module, self.is_plugin)[
                    0
                ]
                plugin_info.plugin_object = plugin_cls()
                self.plugin_registry[plugin_info.identifier] = plugin_info
            except Exception:
                logger.error(f"Unable to create plugin object: {candidate_filepath}")
                continue  # If it didn't work once it wont again


class ConverterPluginManager(BasePluginManager[SVSConverterBase, FormatProviderPluginInfo]):
    pass


class MiddlewareManager(BasePluginManager[MiddlewareBase, MiddlewarePluginInfo]):
    pass


plugin_manager = ConverterPluginManager(
    info_extension="yapsy-plugin",
    plugin_base=SVSConverterBase,  # type: ignore [type-abstract]
    plugin_info_class=FormatProviderPluginInfo,
    plugin_places=[pkg_dir / "plugins", app_dir.user_config_path / "plugins"],
    plugin_namespace="libresvip.plugins",
    install_path=app_dir.user_config_path / "plugins",
)
plugin_manager.import_plugins()
middleware_manager = MiddlewareManager(
    info_extension="yapsy-plugin",
    plugin_base=MiddlewareBase,  # type: ignore [type-abstract]
    plugin_info_class=MiddlewarePluginInfo,
    plugin_places=[
        pkg_dir / "middlewares",
        app_dir.user_config_path / "middlewares",
    ],
    plugin_namespace="libresvip.middlewares",
    install_path=app_dir.user_config_path / "middlewares",
)
middleware_manager.import_plugins()


def merge_translation(
    ori_translation: gettext.NullTranslations,
    resource_dir: Traversable,
    lang: str,
) -> gettext.NullTranslations:
    msg_dir = resource_dir / "locales" / lang / "LC_MESSAGES"
    if msg_dir.is_dir():
        for child_file in msg_dir.iterdir():
            if child_file.name.endswith(".mo"):
                with child_file.open("rb") as fp:
                    child_translation = gettext.GNUTranslations(fp)
                    new_translation = copy.copy(ori_translation)
                    new_translation.add_fallback(child_translation)
                    return new_translation
    else:
        logger.debug(f"No translation file found in {msg_dir}")
    return ori_translation


def get_translation(lang: Optional[str] = None) -> gettext.NullTranslations:
    if lang is None:
        lang = get_ui_settings().language.value
    translation = gettext.NullTranslations()
    translation = merge_translation(translation, res_dir, lang)
    for manager in [plugin_manager, middleware_manager]:
        for plugin_id in manager.plugin_registry:
            plugin_base_dir = package_path(f"{manager.plugin_namespace}.{plugin_id}")
            translation = merge_translation(translation, plugin_base_dir, lang)
    return translation
