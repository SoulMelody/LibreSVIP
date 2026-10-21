"""Pin core dependencies to versions installable by micropip on Pyodide.

micropip resolves the dependencies baked into the libresvip wheel against the
Pyodide build's simple index (https://index.pyodide.org/<version>/). That
index lags PyPI, so a requirement newer than the indexed build of a package
with a native extension makes the wheel uninstallable. Pure-Python wheels are
left alone, whether or not the index carries them: micropip installs those
straight from PyPI.

Only ``project.dependencies`` is touched, and only the lines that are actually
in effect under emscripten (so the ``PyYAML-ft`` line, which excludes
emscripten, stays as it is). Versions are pinned exactly: this file is only
ever used to build the Pyodide wheel.

A few packages do not follow that rule:

- ``charset-normalizer``, ``packaging`` and ``pydantic`` publish pure-Python
  wheels, but each has to stay on the indexed build: ``packaging`` because
  micropip depends on it and a newer build conflicts with the one micropip
  ships, the other two because the build Pyodide tested is the one that works.
- ``cbor2`` 6.x became a Rust extension and publishes no Pyodide wheel, so it
  is pinned to the last pure-Python 5.x release on PyPI.
- ``wanakana-python`` is shipped as a locally built wheel, because PyPI only
  publishes its sdist, and its line is left untouched.
"""

import json
import re
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

import typer
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

INDEX_URL = "https://index.pyodide.org/{version}/{name}/"
USER_AGENT = "LibreSVIP pyodide dependency patcher"

# Shipped as a wheel built locally, because PyPI only publishes its sdist.
LOCAL_WHEELS = {"wanakana-python"}
# Not in the Pyodide index, and not installable from PyPI as-is: cbor2 6.x is a
# Rust extension without a Pyodide wheel, so it stays on the last pure-Python
# 5.x release.
PYPI_PINS = {"cbor2": Version("6")}
# Pure Python, but pinned to the indexed build anyway.
PIN_EVEN_IF_PURE = ["charset-normalizer", "packaging", "pydantic"]

app = typer.Typer()


def _open(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()


def indexed_version(name: str, pyodide_version: str) -> Version | None:
    """Newest indexed build micropip has to install from the index.

    Pure-Python wheels (``py3-none-any``) are ignored, except for the packages
    in ``PIN_EVEN_IF_PURE``.
    """
    try:
        html = _open(INDEX_URL.format(version=pyodide_version, name=name))
    except urllib.error.HTTPError:
        return None
    versions = set()
    for file_name in re.findall(r">([^<]+\.whl)<", html):
        usable = (
            "pyemscripten" in file_name
            or "abi3" in file_name
            or (name in PIN_EVEN_IF_PURE and "py3-none-any" in file_name)
        )
        match = re.search(r"-(\d+(?:\.\d+)+(?:(?:a|b|rc)\d+)?)-", file_name)
        if usable and match:
            versions.add(Version(match.group(1)))
    return max(versions, default=None)


def latest_pypi_version(name: str, below: Version) -> Version | None:
    releases = json.loads(_open(f"https://pypi.org/pypi/{name}/json"))["releases"]
    versions = []
    for version, files in releases.items():
        parsed = Version(version)
        if parsed.is_prerelease or parsed >= below:
            continue
        if any(
            file["packagetype"] == "bdist_wheel" and file["python_version"] in ("py3", "py2.py3")
            for file in files
        ):
            versions.append(parsed)
    return max(versions, default=None)


def pinned_version(name: str, pyodide_version: str) -> Version | None:
    canonical = canonicalize_name(name)
    if canonical in PYPI_PINS:
        return latest_pypi_version(canonical, PYPI_PINS[canonical])
    return indexed_version(canonical, pyodide_version)


def applies_on_emscripten(requirement: Requirement, python_version: str) -> bool:
    return requirement.marker is None or requirement.marker.evaluate(
        {
            "python_version": python_version,
            "python_full_version": f"{python_version}.0",
            "sys_platform": "emscripten",
            "platform_system": "Emscripten",
            "platform_python_implementation": "CPython",
            "os_name": "posix",
            "platform_machine": "wasm32",
        }
    )


@app.command()
def main(
    pyodide_version: str = typer.Option("314.0.7", help="Pyodide build, e.g. 314.0.7."),
    pyproject: Path = typer.Option(Path("pyproject.toml"), help="pyproject.toml to patch."),
    dry_run: bool = typer.Option(False, help="Print the rewritten lines without writing them."),
) -> None:
    """Rewrite core dependency lines for a Pyodide wheel build."""
    python_version = f"{pyodide_version[0]}.{pyodide_version[1 : pyodide_version.index('.')]}"
    document = tomllib.loads(pyproject.read_text())
    lines = pyproject.read_text().splitlines()

    replacements: dict[int, str] = {}
    for dependency in document["project"]["dependencies"]:
        requirement = Requirement(dependency)
        if requirement.name in LOCAL_WHEELS or not applies_on_emscripten(
            requirement, python_version
        ):
            continue
        version = pinned_version(requirement.name, pyodide_version)
        if version is None:
            continue
        pinned = f"{requirement.name}=={version}"
        if requirement.marker is not None:
            pinned += f"; {requirement.marker}"
        quoted = json.dumps(dependency)
        for index, line in enumerate(lines):
            if quoted in line and index not in replacements:
                replacements[index] = line.replace(quoted, json.dumps(pinned))
                break
        else:
            typer.echo(f"skip {requirement.name}: line not found verbatim", err=True)

    for index in sorted(replacements):
        typer.echo(f"{lines[index].strip()}  ->  {replacements[index].strip()}")
        lines[index] = replacements[index]
    if not dry_run:
        pyproject.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    app()
