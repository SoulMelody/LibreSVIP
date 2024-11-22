import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

from loguru import logger
from pip._vendor.packaging.requirements import InvalidRequirement, Requirement

WHEEL_INFO_RE = re.compile(
    r"""^(?P<namever>(?P<name>[^\s-]+?)-(?P<ver>[^\s-]+?))(-(?P<build>\d[^\s-]*))?
     -(?P<pyver>[^\s-]+?)-(?P<abi>[^\s-]+?)-(?P<plat>\S+)\.whl$""",
    re.VERBOSE,
)


def download_win_arm64_web_wheels() -> None:
    cwd = pathlib.Path()

    python_version = "3.12"
    bundle_url = "https://github.com/cgohlke/win_arm64-wheels/releases/download/v2024.11.3/2024.11.3-experimental-cp312-win_arm64.whl.zip"
    bundle_path = pathlib.Path(bundle_url)
    arm64_wheels_archive = cwd / bundle_path.name
    wheels_dir = cwd / bundle_path.with_suffix("").name
    if not wheels_dir.exists():
        if not arm64_wheels_archive.exists():
            with urllib.request.urlopen(bundle_url) as response:
                arm64_wheels_archive.write_bytes(response.read())
        shutil.unpack_archive(arm64_wheels_archive)

    native_packages = {}
    third_party_arm64_packages = {
        "aiohttp": None,
        "lxml": None,
        "markupsafe": None,
        "orjson": None,
        "pyyaml": None,
        "regex": None,
        "ruamel.yaml.clib": "ruamel-yaml-clib",
        "ujson": None,
        "zstandard": None,
    }

    for wheel_path in wheels_dir.glob("*.whl"):
        if (matcher := WHEEL_INFO_RE.match(wheel_path.name)) is not None:
            pkg_name = matcher.group("name").lower()
            if pkg_name in third_party_arm64_packages and not pkg_name.startswith("pydantic"):
                native_packages[third_party_arm64_packages[pkg_name] or pkg_name] = wheel_path

    requirements_path = cwd / "requirements-webui.txt"
    for requirement_str in requirements_path.read_text().splitlines():
        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement:
            continue
        if (
            requirement.marker is None
            or requirement.marker.evaluate(
                environment={
                    "platform_system": "Windows",
                    "platform_machine": "arm64",
                    "python_version": python_version,
                    "sys_platform": "win32",
                }
            )
            is True
        ) and requirement.name != "httptools":
            if requirement.name not in native_packages:
                logger.info(f"Downloading {requirement.name}...")
                try:
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "download",
                            f"{requirement.name}{requirement.specifier}",
                            "--no-deps",
                            "--platform",
                            "win_arm64",
                            "--only-binary",
                            ":all:",
                            "--python-version",
                            python_version,
                        ]
                    )
                except subprocess.CalledProcessError:
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "wheel",
                            f"{requirement.name}{requirement.specifier}",
                            "--no-binary",
                            ":all:",
                        ]
                    )
            else:
                logger.info(f"Using pre-built {requirement.name} wheel...")
                wheel_path = native_packages[requirement.name]
                shutil.copy(wheel_path, cwd / wheel_path.name)


if __name__ == "__main__":
    download_win_arm64_web_wheels()
