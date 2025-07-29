from enum import Enum


class CloudProvider(str, Enum):
    """The cloud service provider offering this GPU instance. Identifies which major cloud platform the instance belongs to."""

    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    OCI = "OCI"
    UNKNOWN = "UNKNOWN"
