import contextlib
import pathlib

import pip
from delocate.fuse import fuse_wheels
from packaging.requirements import InvalidRequirement, Requirement

from libresvip.core.constants import PACKAGE_NAME

if __name__ == "__main__":
    # reference: https://github.com/python-pillow/Pillow/pull/6912/
    macos_platforms = ["macosx_10_10_x86_64", "macosx_11_0_arm64"]
    no_universal2_packages = [
        "pydantic-core",
        "ujson",
        "zstandard",
    ]
    requirements_path = pathlib.Path("requirements.txt")
    new_requirements = []
    for requirement_str in requirements_path.read_text().splitlines():
        try:
            requirement = Requirement(requirement_str)
        except InvalidRequirement:
            continue
        if (
            requirement.marker is None or requirement.marker.evaluate() is True
        ) and requirement.name != PACKAGE_NAME:
            if requirement.name in no_universal2_packages:
                normalized_name = requirement.name.replace("-", "_")
                for macos_platform in macos_platforms:
                    pip.main(
                        [
                            "download",
                            requirement.name,
                            "--platform",
                            macos_platform,
                            "--no-deps",
                            "--only-binary",
                            ":all:",
                        ]
                    )
                universal2_wheel_name = f"{normalized_name}-universal2-.whl"
                with contextlib.suppress(FileNotFoundError):
                    fuse_wheels(
                        *(
                            str(whl_path)
                            for whl_path in pathlib.Path().glob(f"{normalized_name}*.whl")
                        ),
                        universal2_wheel_name,
                    )
                    pip.main("install", universal2_wheel_name, "--no-deps")
            else:
                new_requirements.append(requirement_str)
    new_requirements_path = requirements_path.with_stem("requirements-universal2")
    new_requirements_path.write_text("\n".join(new_requirements))
    pip.main(["install", "-r", str(new_requirements_path)])
