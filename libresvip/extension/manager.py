import contextlib

from yapsy.AutoInstallPluginManager import AutoInstallPluginManager
from yapsy.PluginManager import PluginManager, PluginManagerSingleton

from libresvip.core.constants import app_dir, pkg_dir

from ._patches import LibreSvipPluginFileLocator, LibreSvipPluginInfo
from .base import ReadOnlyConverterBase, SVSConverterBase, WriteOnlyConverterBase

plugin_locator = LibreSvipPluginFileLocator(plugin_info_cls=LibreSvipPluginInfo)
plugin_locator.setPluginPlaces(
    [str(pkg_dir / "plugins"), str(app_dir.user_config_path / "plugins")]
)
PluginManagerSingleton.setBehaviour(
    [
        AutoInstallPluginManager,
    ]
)
plugin_manager: PluginManager = PluginManagerSingleton.get()
plugin_manager.setPluginLocator(plugin_locator)
plugin_manager.setCategoriesFilter(
    categories_filter={
        "writeonly": WriteOnlyConverterBase,
        "svs": SVSConverterBase,
        "readonly": ReadOnlyConverterBase,
    }
)
plugin_manager.setInstallDir(str(app_dir.user_config_path / "plugins"))
plugin_registry = {}


def load_plugins():
    with contextlib.suppress(ValueError):
        plugin_manager.collectPlugins()
    plugin_registry.update(
        {
            plugin_info.suffix: plugin_info
            for plugin_info in plugin_manager.getAllPlugins()
        }
    )


load_plugins()
