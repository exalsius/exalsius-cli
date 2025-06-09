# TODO: both enums currently are not available in the exalsius_api_client package
from enum import Enum


class NodeType(str, Enum):
    """The type of the node."""

    CLOUD = "CLOUD"
    SELF_MANAGED = "SELF_MANAGED"


class CloudProvider(str, Enum):
    """The cloud service provider offering this GPU instance. Identifies which major cloud platform the instance belongs to."""

    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    OCI = "OCI"
    UNKNOWN = "UNKNOWN"
