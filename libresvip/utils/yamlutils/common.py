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
    "1.1": [
        {
            "tag": "tag:yaml.org,2002:bool",
            "regexp": re.compile(
                r"""^(?:yes|Yes|YES|no|No|NO
            |true|True|TRUE|false|False|FALSE
            |on|On|ON|off|Off|OFF)$""",
                re.X,
            ),
            "start_chars": list("yYnNtTfFoO"),
        },
        {
            "tag": "tag:yaml.org,2002:float",
            "regexp": re.compile(
                r"""^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?
            |\.[0-9_]+(?:[eE][-+][0-9]+)?
            |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*
            |[-+]?\.(?:inf|Inf|INF)
            |\.(?:nan|NaN|NAN))$""",
                re.X,
            ),
            "start_chars": list("-+0123456789."),
        },
        {
            "tag": "tag:yaml.org,2002:int",
            "regexp": re.compile(
                r"""^(?:[-+]?0b[0-1_]+
            |[-+]?0[0-7_]+
            |[-+]?(?:0|[1-9][0-9_]*)
            |[-+]?0x[0-9a-fA-F_]+
            |[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$""",
                re.X,
            ),
            "start_chars": list("-+0123456789"),
        },
        {
            "tag": "tag:yaml.org,2002:null",
            "regexp": re.compile(
                r"""^(?: ~
            |null|Null|NULL
            | )$""",
                re.X,
            ),
            "start_chars": ["~", "n", "N", ""],
        },
        {
            "tag": "tag:yaml.org,2002:timestamp",
            "regexp": re.compile(
                r"""^(?:[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]
            |[0-9][0-9][0-9][0-9] -[0-9][0-9]? -[0-9][0-9]?
            (?:[Tt]|[ \t]+)[0-9][0-9]?
            :[0-9][0-9] :[0-9][0-9] (?:\.[0-9]*)?
            (?:[ \t]*(?:Z|[-+][0-9][0-9]?(?::[0-9][0-9])?))?)$""",
                re.X,
            ),
            "start_chars": list("0123456789"),
        },
        {"tag": "tag:yaml.org,2002:value", "regexp": re.compile(r"^(?:=)$"), "start_chars": ["="]},
    ],
    "1.2": [
        {
            "tag": "tag:yaml.org,2002:bool",
            "regexp": re.compile(r"^(?:|true|True|TRUE|false|False|FALSE)$", re.X),
            "start_chars": list("tTfF"),
        },
        {
            "tag": "tag:yaml.org,2002:int",
            "regexp": re.compile(
                r"""^(?:
                # [-+]?0b[0-1_]+ # (base 2)
                 [-+]?0[0-7]+ # (base 8)
                |[-+]?0o[0-7]+ # (base 8)
                |[-+]?(0|[1-9][0-9]*) # (base 10)
                # |[-+]?0[0-7_]+ # (base 8)
                # |[-+]?0o[0-7_]+ # (base 8)
                # |[-+]?(0|[1-9][0-9_]*) # (base 10)
                # |[-+]?0x[0-9a-fA-F_]+ # (base 16)
                # |[-+]?[1-9][0-9_]*(:[0-5]?[0-9])+ # (base 60)
                )$""",
                re.X,
            ),
            "start_chars": list("-+0123456789"),
        },
        {
            "tag": "tag:yaml.org,2002:float",
            "regexp": re.compile(
                r"""^(?:
                 [-+]?([0-9][0-9]*)?\.[0-9.]*([eE][-+][0-9]+)? (base 10)
                |[-+]?[0-9][0-9]*(:[0-5]?[0-9])+\.[0-9]* (base 60)
                # |[-+]?([0-9][0-9_]*)?\.[0-9.]*([eE][-+][0-9]+)? (base 10)
                # |[-+]?[0-9][0-9_]*(:[0-5]?[0-9])+\.[0-9_]* (base 60)
                |[-+]?\.(inf|Inf|INF) # (infinity)
                |\.(nan|NaN|NAN) # (not a number)
                )$""",
                re.X,
            ),
            "start_chars": list("-+0123456789."),
        },
        {
            "tag": "tag:yaml.org,2002:null",
            "regexp": re.compile(r"^(?:~||null|Null|NULL)$", re.X),
            "start_chars": ["~", "n", "N", ""],
        },
    ],
}


def set_yaml_grammar(
    resolver: BaseResolver, grammar_version: str = "1.2", expand_merge_keys: bool = True
) -> None:
    if grammar_version not in core_resolvers:
        msg = f"Unknown grammar version {grammar_version}"
        raise ValueError(msg)
    resolvers = list(core_resolvers[grammar_version])
    if expand_merge_keys:
        resolvers.append(merge_resolver)
    resolver.yaml_implicit_resolvers = {}
    for r in resolvers:
        for start_char in r["start_chars"]:
            resolver.yaml_implicit_resolvers.setdefault(start_char, [])
            resolver.yaml_implicit_resolvers[start_char].append((r["tag"], r["regexp"]))


def hash_key(key: Union[str, bytes]) -> str:
    return b64encode(sha224(key.encode() if isinstance(key, str) else key).digest()).decode()
