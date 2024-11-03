from typing import Any

import yaml
from yaml.tokens import (
    AliasToken,
    AnchorToken,
    FlowMappingEndToken,
    FlowMappingStartToken,
    KeyToken,
    ScalarToken,
    ValueToken,
)

from libresvip.utils.yamlutils.common import hash_key, set_yaml_grammar

try:
    from yaml import CSafeLoader as DefaultSafeLoader
except ImportError:
    from yaml import SafeLoader as DefaultSafeLoader


class CustomLoader(yaml.SafeLoader):
    expand_aliases = False

    def emit_yq_kv(self, key: Any, value: Any, original_token: yaml.tokens.Token) -> None:
        marks = {
            "start_mark": original_token.start_mark,
            "end_mark": original_token.end_mark,
        }
        self.tokens.append(FlowMappingStartToken(**marks))
        self.tokens.append(KeyToken(**marks))
        self.tokens.append(ScalarToken(value=key, plain=True, **marks))
        self.tokens.append(ValueToken(**marks))
        self.tokens.append(ScalarToken(value=value, plain=True, **marks))
        self.tokens.append(FlowMappingEndToken(**marks))

    def fetch_alias(self) -> Any:
        if self.expand_aliases:
            return super().fetch_alias()
        self.save_possible_simple_key()
        self.allow_simple_key = False
        alias_token = self.scan_anchor(AliasToken)
        self.emit_yq_kv("__yq_alias__", alias_token.value, original_token=alias_token)

    def fetch_anchor(self) -> Any:
        if self.expand_aliases:
            return super().fetch_anchor()
        self.save_possible_simple_key()
        self.allow_simple_key = False
        anchor_token = self.scan_anchor(AnchorToken)  # noqa: F841
        # self.emit_yq_kv("__yq_anchor__", anchor_token.value, original_token=anchor_token)


def get_loader(
    use_annotations: bool = False,
    expand_aliases: bool = True,
    expand_merge_keys: bool = True,
) -> yaml.SafeLoader:
    def construct_sequence(loader: yaml.SafeLoader, node: yaml.nodes.SequenceNode) -> list[Any]:
        annotations = []
        for i, v_node in enumerate(node.value):
            if not use_annotations:
                break
            if (
                v_node.tag
                and v_node.tag.startswith("!")
                and not v_node.tag.startswith("!!")
                and len(v_node.tag) > 1
            ):
                annotations.append(f"__yq_tag_{i}_{v_node.tag}__")
            if isinstance(v_node, yaml.nodes.ScalarNode) and v_node.style:
                annotations.append(f"__yq_style_{i}_{v_node.style}__")
            elif (
                isinstance(v_node, (yaml.nodes.SequenceNode, yaml.nodes.MappingNode))
                and v_node.flow_style is True
            ):
                annotations.append("__yq_style_{}_{}__".format(i, "flow"))
        return [loader.construct_object(i) for i in node.value] + annotations

    def construct_mapping(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> dict[Any, Any]:
        loader.flatten_mapping(node)  # TODO: is this needed?
        pairs = []
        for k_node, v_node in node.value:
            key = loader.construct_object(k_node)
            value = loader.construct_object(v_node)
            pairs.append((key, value))
            if not (use_annotations and isinstance(key, (str, bytes))):
                continue
            if (
                v_node.tag
                and v_node.tag.startswith("!")
                and not v_node.tag.startswith("!!")
                and len(v_node.tag) > 1
            ):
                pairs.append((f"__yq_tag_{hash_key(key)}__", v_node.tag))
            if isinstance(v_node, yaml.nodes.ScalarNode) and v_node.style:
                pairs.append((f"__yq_style_{hash_key(key)}__", v_node.style))
            elif (
                isinstance(v_node, (yaml.nodes.SequenceNode, yaml.nodes.MappingNode))
                and v_node.flow_style is True
            ):
                pairs.append((f"__yq_style_{hash_key(key)}__", "flow"))
        return dict(pairs)

    def parse_unknown_tags(loader: yaml.SafeLoader, tag_suffix: str, node: yaml.nodes.Node) -> Any:
        if isinstance(node, yaml.nodes.ScalarNode):
            return loader.construct_scalar(node)
        elif isinstance(node, yaml.nodes.SequenceNode):
            return construct_sequence(loader, node)
        elif isinstance(node, yaml.nodes.MappingNode):
            return construct_mapping(loader, node)

    loader_class = DefaultSafeLoader if expand_aliases else CustomLoader
    loader_class.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    loader_class.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, construct_sequence
    )
    loader_class.add_multi_constructor("", parse_unknown_tags)
    loader_class.yaml_constructors.pop("tag:yaml.org,2002:binary", None)
    loader_class.yaml_constructors.pop("tag:yaml.org,2002:set", None)
    set_yaml_grammar(loader_class, expand_merge_keys=expand_merge_keys)
    return loader_class
