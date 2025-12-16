from enum import StrEnum


class AllowedNodeTypes(StrEnum):
    CLOUD = "cloud"
    SELF_MANAGED = "self_managed"


class AllowedNodeFilterStatuses(StrEnum):
    AVAILABLE = "available"
    ADDED = "added"
    FAILED = "failed"


class AllowedNodeImportTypes(StrEnum):
    SSH = "ssh"
    OFFER = "offer"
