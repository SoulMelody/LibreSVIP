import re
from base64 import b64encode
from hashlib import sha224
from typing import Union

from yaml.resolver import BaseResolver

merge_resolver = {
    "tag": "tag:yaml.org,2002:merge",
    "regexp": re.compile(r"^(?:<<)$"),
    "start_chars": ["<"],
}
core_resolvers = {
    "1.2": [
        {
            "tag": "tag:yaml.org,2002:bool",
            "regexp": re.compile(r"^(?:|true|True|TRUE|false|False|FALSE)$", re.VERBOSE),
            "start_chars": list("tTfF"),
        },
        {
            "tag": "tag:yaml.org,2002:int",
            "regexp": re.compile(r"^(?:|0o[0-7]+|[-+]?(?:[0-9]+)|0x[0-9a-fA-F]+)$", re.VERBOSE),
            "start_chars": list("-+0123456789"),
        },
        {
            "tag": "tag:yaml.org,2002:float",
            "regexp": re.compile(
                r"^(?:[-+]?(?:\.[0-9]+|[0-9]+(\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$",
                re.VERBOSE,
            ),
            "start_chars": list("-+0123456789."),
        },
        {
            "tag": "tag:yaml.org,2002:null",
            "regexp": re.compile(r"^(?:~||null|Null|NULL)$", re.VERBOSE),
            "start_chars": ["~", "n", "N", ""],
        },
    ],
}


def set_yaml_grammar(
    resolver: BaseResolver,
    grammar_version: str = "1.2",
    expand_merge_keys: bool = True,
) -> None:
    if grammar_version not in core_resolvers:
        msg = f"Unknown grammar version {grammar_version}"
        raise ValueError(msg)
    resolvers = list(core_resolvers[grammar_version])
    if expand_merge_keys:
        resolvers.append(merge_resolver)
    resolver.yaml_implicit_resolvers = {}
    for r in resolvers:
        for start_char in r["start_chars"]:  # type: ignore[attr-defined]
            resolver.yaml_implicit_resolvers.setdefault(start_char, [])
            resolver.yaml_implicit_resolvers[start_char].append((r["tag"], r["regexp"]))


def hash_key(key: Union[str, bytes]) -> str:
    return b64encode(sha224(key.encode() if isinstance(key, str) else key).digest()).decode()
