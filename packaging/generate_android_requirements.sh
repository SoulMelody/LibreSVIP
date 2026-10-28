#!/usr/bin/env bash
# Regenerates requirements-android.txt on the fly: the mobile wheels only exist on
# the flet index, so the pinned file is intentionally not tracked in the repository.
set -euo pipefail

cd "$(dirname "$0")"

uv pip compile --python-platform aarch64-linux-android \
    --index https://pypi.flet.dev \
    --extra crypto --extra ujson --extra lxml --extra mobile --extra yaml12 \
    -U --python-version 3.14 --no-annotate --no-header \
    --index-strategy unsafe-first-match \
    ../pyproject.toml --overrides requirements-mobile.in \
    -o requirements-android.txt
