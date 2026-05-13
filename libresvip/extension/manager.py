from __future__ import annotations

import copy
import gettext
import itertools
from importlib.resources import files
from typing import TYPE_CHECKING

from loguru import logger

from libresvip.core.config import get_settings, settings
from libresvip.core.constants import app_dir, pkg_dir, res_dir
from libresvip.extension.vendor import pluginlib

if TYPE_CHECKING:
    from libresvip.core.compat import Traversable
    from libresvip.extension.base import SVSConverter

plugin_manager = pluginlib.PluginLoader(
    paths=[str(pkg_dir / "plugins"), str(app_dir.user_config_path / "plugins")],
    type_filter=["svs"],
    prefix_package="libresvip",
    blacklist=[("svs", each) for each in settings.disabled_plugins],
)
plugin_manager.load_modules()
plugin_manager.loaded = True
middleware_manager = pluginlib.PluginLoader(
    paths=[str(pkg_dir / "middlewares"), str(app_dir.user_config_path / "middlewares")],
    type_filter=["middleware"],
    prefix_package="libresvip",
)
middleware_manager.load_modules()
middleware_manager.loaded = True


_svs_suffix_map: dict[str, type[SVSConverter]] | None = None
_svs_suffix_map_built = False


def _build_svs_suffix_map() -> dict[str, type[SVSConverter]]:
    global _svs_suffix_map, _svs_suffix_map_built
    if _svs_suffix_map_built and _svs_suffix_map is not None:
        return _svs_suffix_map
    suffix_map: dict[str, type[SVSConverter]] = {}
    for plugin in plugin_manager.plugins.get("svs", {}).values():
        for suffix in plugin.info.suffixes:
            if suffix in suffix_map:
                logger.warning(
                    f"Duplicate suffix '{suffix}' declared by plugins '{suffix_map[suffix].__name__}' and '{plugin.__name__}'"
                )
            suffix_map[suffix] = plugin
    _svs_suffix_map = suffix_map
    _svs_suffix_map_built = True
    return suffix_map


def get_svs_plugin_by_suffix(suffix: str) -> type[SVSConverter] | None:
    return _build_svs_suffix_map().get(suffix)


def get_duplicate_suffixes() -> dict[str, list[str]]:
    suffix_to_plugins: dict[str, list[str]] = {}
    for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items():
        for suffix in plugin.info.suffixes:
            suffix_to_plugins.setdefault(suffix, []).append(plugin_id)
    return {suffix: plugins for suffix, plugins in suffix_to_plugins.items() if len(plugins) > 1}


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


def get_translation(lang: str | None = None) -> gettext.NullTranslations:
    if lang is None:
        ui_settings = get_settings()
        lang = ui_settings.language.value
    translation = gettext.NullTranslations()
    translation = merge_translation(translation, res_dir, lang)
    for plugin in itertools.chain(
        plugin_manager.plugins.get("svs", {}).values(),
        middleware_manager.plugins.get("middleware", {}).values(),
    ):
        plugin_base_dir = files(plugin.__module__.rsplit(".", 1)[0])
        translation = merge_translation(translation, plugin_base_dir, lang)
    return translation
