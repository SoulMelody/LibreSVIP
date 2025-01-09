"""modified from distutils.command.bdist_dumb"""

import os
import pathlib
from sysconfig import get_python_version
from typing import ClassVar, Optional

from loguru import logger
from setuptools import Command
from setuptools._distutils.dir_util import ensure_relative, remove_tree
from setuptools._distutils.errors import DistutilsPlatformError
from setuptools._distutils.util import get_platform


class BdistPortable(Command):
    description = 'create a "portable" built distribution'

    user_options: ClassVar[list[tuple[str, Optional[str], str]]] = [
        (
            "bdist-dir=",
            "d",
            "temporary directory for creating the distribution",
        ),
        (
            "plat-name=",
            "p",
            f"platform name to embed in generated filenames (default: {get_platform()})",
        ),
        (
            "format=",
            "f",
            "archive format to create (tar, gztar, bztar, xztar, ztar, zip)",
        ),
        (
            "keep-temp",
            "k",
            "keep the pseudo-installation tree around after " + "creating the distribution archive",
        ),
        ("dist-dir=", "d", "directory to put final built distributions in"),
        (
            "skip-build",
            None,
            "skip rebuilding everything (for testing/debugging)",
        ),
        (
            "relative",
            None,
            "build the archive using relative paths (default: false)",
        ),
        (
            "owner=",
            "u",
            "Owner name used when creating a tar file [default: current user]",
        ),
        (
            "group=",
            "g",
            "Group name used when creating a tar file [default: current group]",
        ),
    ]

    boolean_options: ClassVar[list[str]] = [
        "keep-temp",
        "skip-build",
        "relative",
    ]

    default_format: ClassVar[dict[str, str]] = {"posix": "gztar", "nt": "zip"}

    def initialize_options(self) -> None:
        self.bdist_dir: Optional[pathlib.Path] = None
        self.plat_name = None
        self.format: Optional[str] = None
        self.keep_temp = 0
        self.dist_dir = None
        self.skip_build = None
        self.relative = 0
        self.owner = None
        self.group = None

    def finalize_options(self) -> None:
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command("bdist").bdist_base
            self.bdist_dir = pathlib.Path(bdist_base) / "portable"
        elif not isinstance(self.bdist_dir, pathlib.Path):
            self.bdist_dir = pathlib.Path(self.bdist_dir)

        if self.format is None:
            try:
                self.format = self.default_format[os.name]
            except KeyError as exc:
                msg = f"don't know how to create portable built distributions on platform {os.name}"
                raise DistutilsPlatformError(msg) from exc

        self.set_undefined_options(
            "bdist",
            ("dist_dir", "dist_dir"),
            ("plat_name", "plat_name"),
            ("skip_build", "skip_build"),
        )

    def run(self) -> None:
        if not self.skip_build:
            self.run_command("build")

        install = self.reinitialize_command("install", reinit_subcommands=1)
        install.skip_build = self.skip_build
        install.warn_dir = 0
        install.prefix = "./libresvip"

        install.root = self.bdist_dir
        logger.info("installing to %s", self.bdist_dir)
        self.run_command("install")

        # And make an archive relative to the root of the
        # pseudo-installation tree.
        archive_basename = f"{self.distribution.get_fullname()}.{self.plat_name}"

        pseudoinstall_root = pathlib.Path(self.dist_dir or "./dist") / archive_basename
        if not self.relative:
            archive_root = self.bdist_dir
        elif self.distribution.has_ext_modules() and (
            install.install_base != install.install_platbase
        ):
            msg = f"can't make a portable built distribution where base and platbase are different ({install.install_base!r}, {install.install_platbase!r})"
            raise DistutilsPlatformError(msg)
        else:
            archive_root = self.bdist_dir / ensure_relative(install.install_base)

        # Make the archive
        filename = self.make_archive(
            pseudoinstall_root,
            self.format,
            root_dir=archive_root,
            owner=self.owner,
            group=self.group,
        )
        pyversion = get_python_version() if self.distribution.has_ext_modules() else "any"
        self.distribution.dist_files.append(("bdist_portable", pyversion, filename))

        if not self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)
