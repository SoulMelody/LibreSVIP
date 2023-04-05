import base64
import contextlib
import importlib
import pathlib
import sys
import types

from pkg_resources.extern.packaging.version import Version
from yapsy.AutoInstallPluginManager import AutoInstallPluginManager
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.PluginInfo import PluginInfo
from yapsy.PluginManager import PluginManager

from ..core.constants import app_dir, pkg_dir
from .base import ReadOnlyConverterBase, SVSConverterBase, WriteOnlyConverterBase

plugin_namespace = "libresvip.plugins"


def load_module(name: str, plugin_path: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as e:
        raise ImportError(f"{e.strerror}: {plugin_path}") from e
    return module


def _importModule(plugin_module_name: str, candidate_filepath: str) -> types.ModuleType:
    """
    Import a module, trying either to find it as a single file or as a directory.

    .. note:: Isolated and provided to be reused, but not to be reimplemented !
    """
    # use imp to correctly load the plugin as a module
    candidate_filepath = pathlib.Path(candidate_filepath)

    if candidate_filepath.is_dir():
        candidate_module = load_module(plugin_module_name, candidate_filepath)
    else:
        candidate_filepath = candidate_filepath.with_suffix(".py")
        plugin_dirname = candidate_filepath.parent.name
        plugin_package = f"{plugin_namespace}.{plugin_dirname}"
        package_path = candidate_filepath.parent / "__init__.py"
        if plugin_package not in sys.modules:
            sys.modules[plugin_package] = load_module(plugin_package, package_path)

        candidate_module = load_module(plugin_module_name, candidate_filepath)
    return candidate_module


PluginManager._importModule = _importModule


class LibreSvipPluginInfo(PluginInfo):
    def _get_description(self):
        return (
            self.details.get("Documentation", "Description")
            .encode("raw_unicode_escape")
            .decode("unicode_escape")
        )

    def _set_description(self, description):
        if not self.details.has_section("Documentation"):
            self.details.add_section("Documentation")
        self.details.set("Documentation", "Description", description)

    description = property(_get_description, _set_description)

    def _get_icon_base64(self):
        return self.details.get("Documentation", "IconBase64")

    def _set_icon_base64(self, icon_base64):
        if not self.details.has_section("Documentation"):
            self.details.add_section("Documentation")
        self.details.set(
            "Documentation", "IconBase64", base64.b64encode(icon_base64).decode()
        )

    icon_base64 = property(_get_icon_base64, _set_icon_base64)

    def _get_file_format(self):
        return self.details.get("Documentation", "Format")

    def _set_file_format(self, file_format):
        if not self.details.has_section("Documentation"):
            self.details.add_section("Documentation")
        self.details.set("Documentation", "Format", file_format)

    file_format = property(_get_file_format, _set_file_format)

    def _get_suffix(self):
        return self.details.get("Documentation", "Suffix")

    def _set_suffix(self, suffix):
        if not self.details.has_section("Documentation"):
            self.details.add_section("Documentation")
        self.details.set("Documentation", "Suffix", suffix)

    suffix = property(_get_suffix, _set_suffix)

    def _get_version(self):
        return Version(self.details.get("Documentation", "Version"))

    def _set_version(self, vstring):
        """
        Set the version of the plugin.

        Used by subclasses to provide different handling of the
        version number.
        """
        if isinstance(vstring, Version):
            vstring = str(vstring)
        if not self.details.has_section("Documentation"):
            self.details.add_section("Documentation")
        self.details.set("Documentation", "Version", vstring)

    version = property(_get_version, _set_version)

    def _get_target_framework(self):
        return Version(self.details.get("Documentation", "TargetFramework"))

    def _set_target_framework(self, target_framework):
        if isinstance(target_framework, Version):
            target_framework = str(target_framework)
        if not self.details.has_section("Documentation"):
            self.details.add_section("Documentation")
        self.details.set("Documentation", "TargetFramework", target_framework)

    target_framework = property(_get_target_framework, _set_target_framework)

    @property
    def version_string(self):
        return str(self.version)

    def _ensureDetailsDefaultsAreBackwardCompatible(self):
        if not self.details.has_option("Documentation", "TargetFramework"):
            self.target_framework = "0.0"
        if not self.details.has_option("Documentation", "Format"):
            self.file_format = "*.*"
        if not self.details.has_option("Documentation", "Suffix"):
            self.suffix = "*.*"
        if not self.details.has_option("Documentation", "IconBase64"):
            self.icon_base64 = b""
        super()._ensureDetailsDefaultsAreBackwardCompatible()


plugin_locator = PluginFileLocator(plugin_info_cls=LibreSvipPluginInfo)
plugin_locator.setPluginPlaces(
    [str(pkg_dir / "plugins"), str(app_dir.user_config_path / "plugins")]
)
_plugin_manager = PluginManager(
    categories_filter={
        "writeonly": WriteOnlyConverterBase,
        "svs": SVSConverterBase,
        "readonly": ReadOnlyConverterBase,
    },
    plugin_locator=plugin_locator,
)
plugin_manager = AutoInstallPluginManager(decorated_manager=_plugin_manager)

plugin_manager.setInstallDir(str(app_dir.user_config_path / "plugins"))
with contextlib.suppress(ValueError):
    plugin_manager.collectPlugins()
plugin_registry = {
    plugin_info.suffix: plugin_info for plugin_info in plugin_manager.getAllPlugins()
}
