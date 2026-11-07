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


def _android_abi_aliases(abi: str) -> tuple[str, ...]:
    normalized = abi.lower().replace("-", "_")
    if normalized in {"arm64_v8a", "aarch64", "arm64"}:
        return "arm64-v8a", "aarch64", "arm64"
    if normalized in {"armeabi_v7a", "armv7l", "armv7"}:
        return "armeabi-v7a", "armv7l", "armv7"
    if normalized in {"x86_64", "amd64"}:
        return "x86_64", "amd64"
    if normalized in {"x86", "i686", "i386"}:
        return "x86", "i686", "i386"
    return (abi,)


def android_abi(machine: str) -> str | None:
    """Normalize a machine name to the Android ABI used in release asset names."""
    aliases = _android_abi_aliases(machine)
    abi = aliases[0]
    if abi in {"arm64-v8a", "armeabi-v7a", "x86_64", "x86"}:
        return abi
    return None


def match_android_apk_asset(assets: list[dict[str, Any]], abi: str) -> dict[str, Any] | None:
    """Match the split APK release asset built for the given Android ABI."""
    pattern = f"LibreSVIP-{abi}.apk"
    return next(
        (asset for asset in assets if fnmatch.fnmatch(asset["name"], pattern)),
        None,
    )


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
