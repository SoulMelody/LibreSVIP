from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import yaml

from .common import hash_key, set_yaml_grammar

if TYPE_CHECKING:
    from collections.abc import Iterable

    from _typeshed import SupportsItems


class OrderedIndentlessDumper(yaml.SafeDumper):
    pass


class OrderedDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)

    def ignore_aliases(self, data: Any) -> bool:
        return True


yaml_value_annotation_re = re.compile(r"^__yq_(?P<type>tag|style)_(?P<key>.+)__$")
yaml_item_annotation_re = re.compile(r"^__yq_(?P<type>tag|style)_(?P<key>\d+)_(?P<value>.+)__$")


def get_dumper(
    use_annotations: bool = False,
    indentless: bool = False,
    grammar_version: str = "1.2",
) -> yaml.SafeDumper:
    # if not (use_annotations or indentless):
    #     return default_dumper

    def represent_dict(
        dumper: yaml.SafeDumper, data: SupportsItems[Any, Any]
    ) -> yaml.nodes.MappingNode:
        pairs, custom_styles, custom_tags = [], {}, {}
        for k, v in data.items():
            if use_annotations and isinstance(k, str):
                if k == "__yq_alias__":
                    continue
                value_annotation = yaml_value_annotation_re.match(k)
                if value_annotation and value_annotation.group("type") == "style":
                    custom_styles[value_annotation.group("key")] = v
                    continue
                elif value_annotation and value_annotation.group("type") == "tag":
                    custom_tags[value_annotation.group("key")] = v
                    continue
            pairs.append((k, v))
        mapping = dumper.represent_mapping("tag:yaml.org,2002:map", pairs)
        if use_annotations:
            for k, v in mapping.value:
                hashed_key = hash_key(k.value)
                if hashed_key in custom_styles:
                    if isinstance(v, yaml.nodes.ScalarNode):
                        v.style = custom_styles[hashed_key]
                    elif custom_styles[hashed_key] == "flow":
                        v.flow_style = True
                if hashed_key in custom_tags:
                    v.tag = custom_tags[hashed_key]
        return mapping

    def represent_list(dumper: yaml.SafeDumper, data: Iterable[Any]) -> yaml.nodes.SequenceNode:
        raw_list, custom_styles, custom_tags = [], {}, {}
        for v in data:
            if use_annotations and isinstance(v, str):
                annotation = yaml_item_annotation_re.match(v)
                if annotation and annotation.group("type") == "style":
                    custom_styles[annotation.group("key")] = annotation.group("value")
                    continue
                elif annotation and annotation.group("type") == "tag":
                    custom_tags[annotation.group("key")] = annotation.group("value")
                    continue
            raw_list.append(v)
        sequence = dumper.represent_list(raw_list)
        if use_annotations:
            for i, v in enumerate(sequence.value):
                if str(i) in custom_styles:
                    if isinstance(v, yaml.nodes.ScalarNode):
                        v.style = custom_styles[str(i)]
                    elif custom_styles[str(i)] == "flow":
                        v.flow_style = True
                if str(i) in custom_tags:
                    v.tag = custom_tags[str(i)]
        return sequence

    dumper = OrderedIndentlessDumper if indentless else OrderedDumper
    dumper.add_representer(dict, represent_dict)  # type: ignore[attr-defined]
    dumper.add_representer(list, represent_list)  # type: ignore[attr-defined]
    set_yaml_grammar(dumper, grammar_version=grammar_version)
    return dumper
