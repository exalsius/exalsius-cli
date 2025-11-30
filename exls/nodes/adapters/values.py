from enum import StrEnum


class NodeTypesDTO(StrEnum):
    CLOUD = "cloud"
    SELF_MANAGED = "self_managed"


class AllowedNodeStatusFilter(StrEnum):
    AVAILABLE = "available"
    ADDED = "added"
    FAILED = "failed"


class NodeImportTypeDTO(StrEnum):
    SSH = "ssh"
    OFFER = "offer"
