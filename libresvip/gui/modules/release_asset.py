from __future__ import annotations

import fnmatch
from typing import Any, Protocol


class PlatformUname(Protocol):
    system: str
    machine: str


def _windows_arch_aliases(arch: str) -> tuple[str, ...]:
    normalized_arch = arch.lower()
    if normalized_arch in {"amd64", "x86_64"}:
        return "x86_64", "AMD64", "amd64"
    if normalized_arch in {"arm64", "aarch64"}:
        return "ARM64", "arm64", "aarch64"
    return (arch,)


def match_release_asset(
    assets: list[dict[str, Any]],
    uname: PlatformUname,
    python_compiler: str,
) -> dict[str, Any] | None:
    arch = uname.machine.lower()
    if not arch.endswith("64"):
        return None

    if uname.system == "Windows":
        if python_compiler.startswith("GCC") and "arm" not in arch:
            windows_patterns = [
                "LibreSVIP-msys2-*-*.exe",
                "LibreSVIP-*.msys2-*.7z",
            ]
        else:
            arch_aliases = _windows_arch_aliases(arch)
            windows_patterns = [
                pattern
                for arch_alias in arch_aliases
                for pattern in (
                    f"LibreSVIP-*.win-{arch_alias}.*",
                    f"LibreSVIP-*-{arch_alias}.exe",
                )
            ]
        return next(
            (
                asset
                for asset in assets
                if any(fnmatch.fnmatch(asset["name"], pattern) for pattern in windows_patterns)
            ),
            None,
        )

    if "aarch" in arch and uname.system != "Linux":
        return None

    if uname.system == "Linux":
        return next(
            (
                asset
                for asset in assets
                if fnmatch.fnmatch(
                    asset["name"],
                    f"LibreSVIP-*.linux-{arch}.tar.gz",
                )
                or fnmatch.fnmatch(
                    asset["name"],
                    f"LibreSVIP-*-{arch}.AppImage",
                )
            ),
            None,
        )

    if uname.system == "Darwin":
        return next(
            (
                asset
                for asset in assets
                if fnmatch.fnmatch(
                    asset["name"],
                    f"LibreSVIP-*.macos-{arch}.dmg",
                )
            ),
            None,
        )

    return None
