from typing import List, Optional, cast

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import Cluster, ClusterNode
from exls.clusters.core.requests import ClusterDeployRequest


class ClusterNodeIssue(BaseModel):
    node: Optional[ClusterNode] = Field(default=None, description="The node, if known")
    error_message: StrictStr = Field(..., description="The error message that occurred")


class ClusterNodesResult(BaseModel):
    nodes: List[ClusterNode] = Field(..., description="The loaded nodes")
    issues: Optional[List[ClusterNodeIssue]] = Field(
        default=None, description="List of loading issues encountered"
    )

    @property
    def is_success(self) -> bool:
        return self.issues is None or len(self.issues) == 0


class DeployClusterIssue(BaseModel):
    cluster_deploy_request: Optional[ClusterDeployRequest] = Field(
        default=None, description="The created cluster specification"
    )
    cluster_nodes_result: Optional[ClusterNodesResult] = Field(
        default=None, description="The result of the cluster nodes"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")

    # TODO: Add logic hierarchy of issues checking for cluster and cluster nodes


class DeployClusterResult(BaseModel):
    deployed_cluster: Optional[Cluster] = Field(
        default=None, description="The deployed cluster with its nodes"
    )
    issues: List[ClusterNodeIssue] = Field(
        default_factory=lambda: cast(List[ClusterNodeIssue], []),
        description="List of issues encountered",
    )

    @property
    def is_success(self) -> bool:
        return self.deployed_cluster is not None and len(self.issues) == 0

    @property
    def is_partially_successful(self) -> bool:
        return self.deployed_cluster is not None and len(self.issues) > 0


class ClusterScaleIssue(BaseModel):
    node: Optional[ClusterNode] = Field(
        default=None, description="The node that was added"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")


class ClusterScaleResult(BaseModel):
    nodes: List[ClusterNode] = Field(..., description="The added nodes")
    issues: Optional[List[ClusterScaleIssue]] = Field(
        default=None, description="List of issues encountered"
    )
