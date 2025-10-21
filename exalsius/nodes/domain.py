from datetime import datetime
from enum import StrEnum
from typing import Optional

from exalsius_api_client.models.cloud_node import CloudNode as SdkCloudNode
from exalsius_api_client.models.self_managed_node import (
    SelfManagedNode as SdkSelfManagedNode,
)
from pydantic import BaseModel, Field, StrictInt, StrictStr


class NodeType(StrEnum):
    """The type of the node."""

    CLOUD = "CLOUD"
    SELF_MANAGED = "SELF_MANAGED"


class CloudProvider(StrEnum):
    """The provider of the node."""

    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"


class NodeFilterParams(BaseModel):
    """Domain object representing query parameters for nodes."""

    node_type: Optional[NodeType] = Field(
        default=None, description="The type of the node"
    )
    provider: Optional[CloudProvider] = Field(
        default=None, description="The provider of the node"
    )


class ImportSshParams(BaseModel):
    """Domain object representing parameters for importing a self-managed node."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The ID of the SSH key to use")


class ImportFromOfferParams(BaseModel):
    """Domain object representing parameters for importing a node from an offer."""

    hostname: StrictStr = Field(..., description="The hostname of the node")
    offer_id: StrictStr = Field(..., description="The ID of the offer to use")
    amount: StrictInt = Field(..., description="The amount of nodes to import")


class BaseNode(BaseModel):
    """Domain object representing a node."""

    @property
    def id(self) -> StrictStr:
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def hostname(self) -> Optional[StrictStr]:
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def import_time(self) -> Optional[datetime]:
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def node_status(self) -> StrictStr:
        raise NotImplementedError("Subclasses must implement this method")


class CloudNode(BaseNode):
    """Domain object representing a cloud node."""

    sdk_model: SdkCloudNode = Field(..., description="The SDK model of the cloud node")

    @property
    def id(self) -> StrictStr:
        return self.sdk_model.id

    @property
    def hostname(self) -> Optional[StrictStr]:
        return self.sdk_model.hostname

    @property
    def import_time(self) -> Optional[datetime]:
        return self.sdk_model.import_time

    @property
    def node_status(self) -> StrictStr:
        return self.sdk_model.node_status

    @property
    def provider(self) -> StrictStr:
        return self.sdk_model.provider

    @property
    def instance_type(self) -> StrictStr:
        return self.sdk_model.instance_type

    @property
    def price_per_hour(self) -> Optional[StrictStr]:
        return f"{self.sdk_model.price_per_hour:.2f}"


class SelfManagedNode(BaseNode):
    """Domain object representing a self-managed node."""

    sdk_model: SdkSelfManagedNode = Field(
        ..., description="The SDK model of the self-managed node"
    )

    @property
    def id(self) -> StrictStr:
        return self.sdk_model.id

    @property
    def hostname(self) -> Optional[StrictStr]:
        return self.sdk_model.hostname

    @property
    def import_time(self) -> Optional[datetime]:
        return self.sdk_model.import_time

    @property
    def node_status(self) -> StrictStr:
        return self.sdk_model.node_status

    @property
    def endpoint(self) -> Optional[StrictStr]:
        return self.sdk_model.endpoint
