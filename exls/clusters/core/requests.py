from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import ClusterNodeRole, ClusterType


class SshKeySpecification(BaseModel):
    name: StrictStr = Field(..., description="The name of the SSH key")
    key_path: Path = Field(..., description="The path to the SSH key file")


class NodeSpecification(BaseModel):
    hostname: StrictStr = Field(..., description="The hostname of the node")
    endpoint: StrictStr = Field(..., description="The endpoint of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key: Union[StrictStr, SshKeySpecification] = Field(
        ..., description="The SSH key to use"
    )
    role: ClusterNodeRole = Field(..., description="The role of the node")


class ClusterDeployRequest(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
    colony_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the colony to add the cluster to"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None, description="The date and time the cluster will be deleted"
    )
    worker_nodes: List[Union[StrictStr, NodeSpecification]] = Field(
        ..., description="The IDs of the worker nodes"
    )
    control_plane_nodes: Optional[List[Union[StrictStr, NodeSpecification]]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )
    enable_multinode_training: bool = Field(
        ..., description="Enable multinode AI model training for the cluster"
    )
    enable_telemetry: bool = Field(..., description="Enable telemetry for the cluster")
    enable_vpn: bool = Field(..., description="Enable VPN for the cluster")


class NodeRef(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    role: ClusterNodeRole = Field(..., description="The role of the node")


class AddNodesRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    nodes_to_add: List[NodeRef] = Field(
        ..., description="The nodes to add to the cluster"
    )


class RemoveNodesRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    nodes_to_remove: List[NodeRef] = Field(
        ..., description="The nodes to remove from the cluster"
    )
