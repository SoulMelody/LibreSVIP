import dataclasses
import functools
import inspect
import pathlib
import sys
import types
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, PathFinder, SourceFileLoader, all_suffixes
from importlib.util import module_from_spec, spec_from_file_location
from types import ModuleType
from typing import Optional, cast

from loguru import logger
from typing_extensions import TypeGuard

from libresvip.core.compat import Traversable
from libresvip.core.config import settings
from libresvip.core.constants import app_dir, pkg_dir

from .base import BasePlugin, SVSConverterBase
from .meta_info import LibreSvipPluginInfo, PluginInfo

# import zipfile


def load_module(name: str, plugin_path: pathlib.Path) -> types.ModuleType:
    spec = spec_from_file_location(name, plugin_path)
    spec.submodule_search_locations = [str(plugin_path.parent)]
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        msg = f"{e}: {plugin_path}"
        raise ImportError(msg) from e
    return module


@dataclasses.dataclass
class PluginManager:
    info_extension: str
    info_cls: type[PluginInfo]
    plugin_base: type[BasePlugin]
    plugin_namespace: str
    install_path: pathlib.Path
    plugin_places: list[Traversable]
    plugin_registry: dict[str, PluginInfo] = dataclasses.field(default_factory=dict)
    _candidates: list[tuple[str, pathlib.Path, LibreSvipPluginInfo]] = dataclasses.field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        sys.meta_path.append(cast(MetaPathFinder, self))

    @functools.cached_property
    def lib_suffixes(self) -> list[str]:
        return all_suffixes()

    def find_spec(
        self, fullname: str, path: Optional[list[str]], target: Optional[ModuleType] = None
    ) -> Optional[ModuleSpec]:
        if not fullname.startswith(self.plugin_namespace) or not path:
            return None
        path = [str(path) for path in self.plugin_places]

        spec = PathFinder.find_spec(fullname, path, target)
        if spec:
            spec.loader = SourceFileLoader(spec.loader.name, spec.loader.path)
        return spec

    def is_plugin(self, member: object) -> TypeGuard[BasePlugin]:
        return (
            inspect.isclass(member)
            and issubclass(member, self.plugin_base)
            and member != self.plugin_base
        )

    def _import_module(
        self, plugin_module_name: str, candidate_filepath: pathlib.Path, reload: bool
    ) -> types.ModuleType:
        """
        Import a module, trying either to find it as a single file or as a directory.

        .. note:: Isolated and provided to be reused, but not to be reimplemented !
        """

        if not candidate_filepath.is_dir():
            plugin_dirname = candidate_filepath.parent.name
            plugin_package = f"{self.plugin_namespace}.{plugin_dirname}"
            if entry_suffix := next(
                (
                    suffix
                    for suffix in self.lib_suffixes
                    if (candidate_filepath.with_suffix(suffix).is_file())
                ),
                None,
            ):
                candidate_filepath = candidate_filepath.with_suffix(entry_suffix)
            else:
                msg = f"Cannot find a valid entry point for {plugin_module_name} in {candidate_filepath}"
                raise ImportError(
                    msg,
                )
        if plugin_package not in sys.modules or reload:
            sys.modules[plugin_package] = load_module(plugin_package, candidate_filepath)

        return sys.modules[plugin_package]

    def scan_candidates(self) -> None:
        self._candidates.clear()
        _discovered = set()
        for dir_path in self.plugin_places:
            # first of all, is it a directory :)
            if not dir_path.is_dir():
                logger.debug(f"{self.__class__.__name__} skips {dir_path} (not a directory)")
                continue
            # iteratively walks through the directory
            for file_path in dir_path.glob(f"*/*.{self.info_extension}"):
                if (candidate_infofile := str(file_path)) in _discovered:
                    # logger.debug("%s (with strategy %s) rejected because already discovered" % (candidate_infofile, analyzer.name))
                    continue
                # logger.debug("%s found a candidate:\n    %s" % (self.__class__.__name__, candidate_infofile))
                if (plugin_info := self.info_cls.load(file_path)) is None:
                    # logger.debug("Plugin candidate '%s'  rejected by strategy '%s'" % (candidate_infofile, analyzer.name))
                    continue  # we consider this was the good strategy to use for: it failed -> not a plugin -> don't try another strategy
                plugin_info_path = file_path.parent / plugin_info.module
                if (
                    (entry_suffix := plugin_info_path.suffix) in self.lib_suffixes
                    and plugin_info_path.is_file()
                ) or (
                    entry_suffix := next(
                        (
                            suffix
                            for suffix in self.lib_suffixes
                            if (plugin_info_path.with_suffix(suffix).is_file())
                        ),
                        None,
                    )
                ):
                    candidate_filepath = plugin_info_path
                    if candidate_filepath.suffix in self.lib_suffixes:
                        candidate_filepath = candidate_filepath.with_suffix("")
                    _discovered.add(
                        str(
                            plugin_info_path.with_suffix(entry_suffix),
                        )
                    )
                else:
                    logger.error(
                        f"Plugin candidate rejected: cannot find the file or directory module for '{candidate_infofile}'",
                    )
                    break
                self._candidates.append((candidate_infofile, candidate_filepath, plugin_info))
                # finally the candidate_infofile must not be discovered again
                _discovered.add(candidate_infofile)

    def import_plugins(self, reload: bool = False) -> None:
        if reload:
            self.plugin_registry.clear()
        self.scan_candidates()
        for candidate_infofile, candidate_filepath, plugin_info in self._candidates:
            # make sure to attribute a unique module name to the one
            # that is about to be loaded
            plugin_module_name = f"{self.plugin_namespace}.{plugin_info.suffix}"
            if (
                plugin_info.suffix in self.plugin_registry and not reload
            ) or plugin_info.suffix in settings.disabled_plugins:
                logger.debug(f"Skipped plugin: {plugin_info.suffix}")
                continue
            # tolerance on the presence (or not) of the py extensions
            if candidate_filepath.suffix in self.lib_suffixes:
                candidate_filepath = candidate_filepath.with_suffix("")
            # cover the case when the __init__ of a package has been
            # explicitely indicated
            if candidate_filepath.stem == "__init__":
                candidate_filepath = candidate_filepath.parent
            try:
                candidate_module = self._import_module(
                    plugin_module_name, candidate_filepath, reload
                )
            except Exception:
                logger.exception(
                    f"Unable to import plugin: {candidate_filepath}",
                )
                continue

            try:
                plugin_cls_name, plugin_cls = inspect.getmembers(candidate_module, self.is_plugin)[
                    0
                ]
                plugin_info.plugin_object = plugin_cls()
                self.plugin_registry[plugin_info.suffix] = plugin_info
            except Exception:
                logger.exception(f"Unable to create plugin object: {candidate_filepath}")
                continue  # If it didn't work once it wont again


plugin_manager = PluginManager(
    info_extension="yapsy-plugin",
    info_cls=LibreSvipPluginInfo,
    plugin_base=SVSConverterBase,
    plugin_places=[pkg_dir / "plugins", app_dir.user_config_path / "plugins"],
    plugin_namespace="libresvip.plugins",
    install_path=app_dir.user_config_path / "plugins",
)
plugin_manager.import_plugins()
