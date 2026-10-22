"""Drop the `.proto` excerpts protoc-gen-py embeds in generated stubs.

protoc-gen-py renders every message/enum as a docstring holding its proto
source. The excerpts are redundant — the schemas live in
`libresvip/res/protos/` — and they inflate the generated modules, so the
generator script pipes its output through this filter.
"""

from __future__ import annotations

import pathlib
import re
import sys

from loguru import logger

DOCSTRING = re.compile(r'\n[ \t]*"""(?:[^"]|"(?!""))*"""\n', re.DOTALL)
PROTO_EXCERPT = "```proto"


def strip(path: pathlib.Path) -> int:
    source = path.read_text(encoding="utf-8")
    matches = 0

    def drop(match: re.Match[str]) -> str:
        nonlocal matches
        if PROTO_EXCERPT in match.group():
            matches += 1
            return "\n"
        return match.group()

    path.write_text(DOCSTRING.sub(drop, source), encoding="utf-8")
    return matches


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        target = pathlib.Path(argument)
        logger.info(f"{target}: removed {strip(target)} proto docstrings")
