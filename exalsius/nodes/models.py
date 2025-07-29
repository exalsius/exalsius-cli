from enum import Enum


class NodeType(str, Enum):
    """The type of the node."""

    CLOUD = "CLOUD"
    SELF_MANAGED = "SELF_MANAGED"
