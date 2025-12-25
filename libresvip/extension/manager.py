from __future__ import annotations

import copy
import gettext
import itertools
import traceback
from importlib.resources import files
from typing import TYPE_CHECKING

from loguru import logger

from libresvip.core.config import get_ui_settings, settings
from libresvip.core.constants import app_dir, pkg_dir, res_dir
from libresvip.extension.vendor import pluginlib

if TYPE_CHECKING:
    from libresvip.core.compat import Traversable

plugin_manager = pluginlib.PluginLoader(
    paths=[str(pkg_dir / "plugins"), str(app_dir.user_config_path / "plugins")],
    type_filter=["svs"],
    prefix_package="libresvip",
    blacklist=[("svs", each) for each in settings.disabled_plugins],
)
try:
    plugin_manager.load_modules()
except pluginlib.PluginImportError as e:
    logger.error(f"Unable to import plugin: {e}")
    logger.error(traceback.format_exc())
    plugin_manager.loaded = True
middleware_manager = pluginlib.PluginLoader(
    paths=[str(pkg_dir / "middlewares"), str(app_dir.user_config_path / "middlewares")],
    type_filter=["middleware"],
    prefix_package="libresvip",
)
try:
    middleware_manager.load_modules()
except pluginlib.PluginImportError as e:
    logger.error(f"Unable to import middleware plugin: {e}")
    middleware_manager.loaded = True


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
        lang = get_ui_settings().language.value
    translation = gettext.NullTranslations()
    translation = merge_translation(translation, res_dir, lang)
    for plugin in itertools.chain(
        plugin_manager.plugins.get("svs", {}).values(),
        middleware_manager.plugins.get("middleware", {}).values(),
    ):
        plugin_base_dir = files(plugin.__module__.rsplit(".", 1)[0])
        translation = merge_translation(translation, plugin_base_dir, lang)
    return translation
