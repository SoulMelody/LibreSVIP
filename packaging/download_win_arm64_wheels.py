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


def download_win_arm64_wheels() -> None:
    cwd = pathlib.Path()

    python_version = "3.13"

    native_packages = {}
    third_party_arm64_packages = {
        "protobuf": None,
        "pyyaml_ft": "pyyaml-ft",
        "ruamel_yaml_clib": "ruamel-yaml-clib",
    }

    def collect_wheels(bundle_url: str) -> None:
        bundle_path = pathlib.Path(bundle_url)
        arm64_wheels_archive = cwd / bundle_path.name
        wheels_dir = cwd / bundle_path.with_suffix("").with_suffix("").name
        if not wheels_dir.exists():
            if not arm64_wheels_archive.exists():
                with urllib.request.urlopen(bundle_url) as response:
                    arm64_wheels_archive.write_bytes(response.read())
            shutil.unpack_archive(arm64_wheels_archive, wheels_dir)

        for wheel_path in wheels_dir.rglob("*.whl"):
            if (matcher := WHEEL_INFO_RE.match(wheel_path.name)) is not None:
                pkg_name = matcher.group("name").lower()
                if pkg_name in third_party_arm64_packages and not pkg_name.startswith("pydantic"):
                    native_packages[third_party_arm64_packages[pkg_name] or pkg_name] = wheel_path

    for bundle_url in [
        "https://github.com/cgohlke/win_arm64-wheels/releases/download/v2025.7.7/2025.7.7-experimental-cp313-win_arm64.whl.zip",
    ]:
        collect_wheels(bundle_url)

    requirements_path = cwd / "requirements-desktop.txt"
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
        ):
            if requirement.name not in native_packages:
                download_url = f"{requirement.name}{requirement.specifier}"
                logger.info(f"Downloading {requirement.name}...")
                try:
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "download",
                            download_url,
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
    download_win_arm64_wheels()
