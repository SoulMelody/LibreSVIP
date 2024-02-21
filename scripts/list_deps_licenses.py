import contextlib
import importlib.metadata
import re

import click
import httpx
from packaging.requirements import Requirement

GITHUB_REPO_URL = re.compile(r"^(?:https?://)?(?:www\.)?github\.com/([^/]+/[^/]+)")


def find_license_from_metadata(home_page_urls: list[str], classifiers: list[str]) -> str:
    licenses = []
    for classifier in filter(lambda c: c.startswith("License"), classifiers):
        license_str = classifier.rpartition(" :: ")[-1]

        # Through the declaration of 'Classifier: License :: OSI Approved'
        if license_str != "OSI Approved" and license_str and not license_str.startswith("Other"):
            licenses.append(license_str)

    if not licenses:
        for url in home_page_urls:
            if (github_repo := GITHUB_REPO_URL.match(url)) is not None:
                owner_repo = github_repo.group(1)
                if owner_repo == "starwort/wanakana":
                    owner_repo = "Starwort/wanakana-py"
                license_api_url = f"https://api.github.com/repos/{owner_repo}/license"
                if not (response := httpx.get(license_api_url)).is_error:
                    license_data = response.json()
                    if (license_str := license_data.get("license", {}).get("name")) is not None:
                        return license_str

    return "; ".join(licenses or ["UNKNOWN"])


if __name__ == "__main__":
    distribution = None
    with contextlib.suppress(importlib.metadata.PackageNotFoundError):
        distribution = importlib.metadata.distribution("libresvip")

    if distribution is not None and distribution.requires is not None:
        for require in distribution.requires:
            req = Requirement(require)
            with contextlib.suppress(importlib.metadata.PackageNotFoundError):
                dep = importlib.metadata.distribution(req.name)
                classifiers = dep.metadata.get_all("classifier")

                if classifiers is not None and dep.name != "libresvip":
                    click.echo(
                        f"{dep.name}: {find_license_from_metadata(dep.metadata.get_all('home-page') or [], classifiers)}"
                    )
