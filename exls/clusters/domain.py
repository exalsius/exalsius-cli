from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Optional

from exalsius_api_client.models.cluster import Cluster as SdkCluster
from exalsius_api_client.models.hardware import Hardware as SdkResourcePool
from pydantic import BaseModel, Field, StrictInt, StrictStr


class ClusterNodeRole(StrEnum):
    WORKER = "worker"
    CONTROL_PLANE = "control-plane"


class Cluster(BaseModel):
    sdk_model: SdkCluster = Field(..., description="The SDK model of the cluster")

    @property
    def id(self) -> StrictStr:
        if self.sdk_model.id is None:
            raise ValueError("ID is None")
        return self.sdk_model.id

    @property
    def name(self) -> StrictStr:
        return self.sdk_model.name

    @property
    def cluster_status(self) -> StrictStr:
        return self.sdk_model.cluster_status

    @property
    def created_at(self) -> datetime:
        return self.sdk_model.created_at

    @property
    def updated_at(self) -> Optional[datetime]:
        return self.sdk_model.updated_at


class Resources(BaseModel):
    sdk_model: SdkResourcePool = Field(
        ..., description="The SDK model of the resources"
    )

    @property
    def gpu_type(self) -> Optional[StrictStr]:
        return self.sdk_model.gpu_type

    @property
    def gpu_vendor(self) -> Optional[StrictStr]:
        return self.sdk_model.gpu_vendor

    @property
    def gpu_count(self) -> StrictInt:
        if self.sdk_model.gpu_count is None:
            return 0
        return self.sdk_model.gpu_count

    @property
    def cpu_cores(self) -> StrictInt:
        if self.sdk_model.cpu_cores is None:
            return 0
        return self.sdk_model.cpu_cores

    @property
    def memory_gb(self) -> StrictInt:
        if self.sdk_model.memory_gb is None:
            return 0
        return self.sdk_model.memory_gb

    @property
    def storage_gb(self) -> StrictInt:
        if self.sdk_model.storage_gb is None:
            return 0
        return self.sdk_model.storage_gb


class ClusterNodeResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )


class ClusterNodeRef(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    role: StrictStr = Field(..., description="The role of the node")
