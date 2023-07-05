import base64
import configparser
import importlib.util
import io
import pathlib
import sys
import types
from importlib.machinery import PathFinder, SourceFileLoader, all_suffixes

from loguru import logger
from setuptools.extern.packaging.version import Version
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.PluginInfo import PluginInfo
from yapsy.PluginManager import PluginManager

from libresvip.core.constants import app_dir, pkg_dir

plugin_namespace = "libresvip.plugins"


class LibreSvipExtraImporter:
    def __init__(self, plugin_namespace):
        self.plugin_namespace = plugin_namespace

    def find_spec(self, fullname, path, target=None):
        if (
            not fullname.startswith(self.plugin_namespace)
            or not path
            or path[0] != str(pkg_dir / "plugins")
        ):
            return None
        path.append(str(app_dir.user_config_path / "plugins"))

        spec = PathFinder.find_spec(fullname, path, target)
        if spec:
            spec.loader = SourceFileLoader(spec.loader.name, spec.loader.path)
        return spec


sys.meta_path.append(LibreSvipExtraImporter(plugin_namespace))


def read_file(self: configparser.ConfigParser, f: io.TextIOWrapper, source=None):
    """Like read() but the argument must be a file-like object.

    The `f' argument must be iterable, returning one line at a time.
    Optional second argument is the `source' specifying the name of the
    file being read. If not given, it is taken from f.name. If `f' has no
    `name' attribute, `<???>' is used.
    """
    if source is None:
        try:
            source = f.name
        except AttributeError:
            source = "<???>"
    if not isinstance(f, io.StringIO):
        content = f.buffer.read()
        string = content.decode("utf-8")
        self.read_string(string)
    else:
        self._read(f, source)


configparser.ConfigParser.read_file = read_file


def load_module(name: str, plugin_path: pathlib.Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, plugin_path)
    spec.submodule_search_locations = [
        str(plugin_path.parent),
    ]
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
    candidate_filepath = pathlib.Path(candidate_filepath)

    if not candidate_filepath.is_dir():
        plugin_dirname = candidate_filepath.parent.name
        plugin_package = f"{plugin_namespace}.{plugin_dirname}"
        if (source_path := candidate_filepath.with_suffix(".py")).exists():
            candidate_filepath = source_path
        else:
            candidate_filepath = candidate_filepath.with_suffix(".pyc")
    if plugin_package not in sys.modules:
        sys.modules[plugin_package] = load_module(plugin_package, candidate_filepath)

    return sys.modules[plugin_package]


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


class LibreSvipPluginFileLocator(PluginFileLocator):
    def locatePlugins(self):
        """
        Walk through the plugins' places and look for plugins.

        Return the candidates and number of plugins found.
        """
        _candidates = []
        _discovered = {}
        lib_suffixes = all_suffixes()
        for directory in self.plugins_places:
            dir_path = pathlib.Path(directory).absolute()
            # first of all, is it a directory :)
            if not dir_path.is_dir():
                logger.debug(f"{self.__class__.__name__} skips {directory} (not a directory)")
                continue
            walk_iter = dir_path.rglob("*") if self.recursive else dir_path.glob("*")
            # iteratively walks through the directory
            for file_path in walk_iter:
                for analyzer in self._analyzers:
                    filename = file_path.name
                    # eliminate the obvious non plugin files
                    if not analyzer.isValidPlugin(filename):
                        # logger.debug("%s is not a valid plugin for strategy %s" % (filename, analyzer.name))
                        continue
                    candidate_infofile = str(file_path)
                    if candidate_infofile in _discovered:
                        # logger.debug("%s (with strategy %s) rejected because already discovered" % (candidate_infofile, analyzer.name))
                        continue
                    # logger.debug("%s found a candidate:\n    %s" % (self.__class__.__name__, candidate_infofile))
                    plugin_info = self._getInfoForPluginFromAnalyzer(analyzer, str(
                        file_path.parent
                    ), filename)
                    if plugin_info is None:
                        # logger.debug("Plugin candidate '%s'  rejected by strategy '%s'" % (candidate_infofile, analyzer.name))
                        break # we consider this was the good strategy to use for: it failed -> not a plugin -> don't try another strategy
                    # now determine the path of the file to execute,
                    # depending on wether the path indicated is a
                    # directory or a file
                    # Remember all the files belonging to a discovered
                    # plugin, so that strategies (if several in use) won't
                    # collide
                    plugin_info_path = pathlib.Path(plugin_info.path)
                    if plugin_info_path.is_dir():
                        candidate_filepath = plugin_info_path / "__init__"
                        # it is a package, adds all the files concerned
                        for _file in plugin_info_path.glob("*.py"):
                            self._discovered_plugins[str(_file)] = candidate_filepath
                            _discovered[str(_file)] = candidate_filepath
                    elif ((entry_suffix := plugin_info_path.suffix) in lib_suffixes and plugin_info_path.is_file()) or (
                        entry_suffix := next(
                            (
                                suffix
                                for suffix in lib_suffixes
                                if (plugin_info_path.with_suffix(suffix).is_file())
                            ),
                            None,
                        )
                    ):
                        candidate_filepath = plugin_info_path
                        if candidate_filepath.suffix in lib_suffixes:
                            candidate_filepath = candidate_filepath.with_suffix("")
                        candidate_filepath = str(candidate_filepath)
                        # it is a file, adds it
                        self._discovered_plugins[str(
                            plugin_info_path.with_suffix(entry_suffix)
                        )] = candidate_filepath
                        _discovered[str(
                            plugin_info_path.with_suffix(entry_suffix)
                        )] = candidate_filepath
                    else:
                        logger.error(
                            f"Plugin candidate rejected: cannot find the file or directory module for '{candidate_infofile}'"
                        )
                        break
                    _candidates.append((candidate_infofile, candidate_filepath, plugin_info))
                    # finally the candidate_infofile must not be discovered again
                    _discovered[candidate_infofile] = candidate_filepath
                    self._discovered_plugins[candidate_infofile] = candidate_filepath
        return _candidates, len(_candidates)
