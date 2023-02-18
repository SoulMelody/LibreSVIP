from xml.dom import minidom

from .vsqx3 import VSQ3_NS
from .vsqx4 import VSQ4_NS


def judge_vsqx_version(vsqx_path: str):
    dom = minidom.parse(vsqx_path)
    namespace = dom.documentElement.namespaceURI
    if namespace == VSQ4_NS:
        return "vsqx4"
    elif namespace == VSQ3_NS:
        return "vsqx3"
    else:
        raise ValueError(f"Unknown vsqx version: {namespace}")
