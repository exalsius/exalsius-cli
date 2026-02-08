from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import (
    Cluster,
    ClusterStatus,
    ClusterSummary,
    ClusterType,
)


class ClusterCreateParameters(BaseModel):
    """Domain object representing parameters for creating a cluster."""

    name: StrictStr = Field(..., description="The name of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
    enable_vpn: bool = Field(..., description="Enable VPN for the cluster")
    enable_telemetry: bool = Field(..., description="Enable telemetry for the cluster")
    enable_multinode_training: bool = Field(
        ..., description="Enable multinode AI model training for the cluster"
    )
    prepare_llm_inference_environment: bool = Field(
        ..., description="Prepare LLM inference environment for the cluster"
    )
    colony_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the colony to add the cluster to"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None, description="The date and time the cluster will be deleted"
    )
    worker_node_ids: List[StrictStr] = Field(
        ..., description="The IDs of the worker nodes"
    )
    control_plane_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )


class ClusterRepository(ABC):
    @abstractmethod
    def list(self, status: Optional[ClusterStatus]) -> List[ClusterSummary]: ...

    @abstractmethod
    def get(self, cluster_id: str) -> Cluster: ...

    @abstractmethod
    def create(self, parameters: ClusterCreateParameters) -> str: ...

    @abstractmethod
    def delete(self, cluster_id: str) -> str: ...
