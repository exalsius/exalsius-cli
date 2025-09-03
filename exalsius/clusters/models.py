import datetime
from enum import Enum, StrEnum
from typing import Dict, List, Optional

from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.cluster_add_node_request import ClusterAddNodeRequest
from exalsius_api_client.models.cluster_create_request import ClusterCreateRequest
from exalsius_api_client.models.cluster_node_to_add import ClusterNodeToAdd
from pydantic import BaseModel, Field

from exalsius.core.base.models import BaseRequestDTO


class ClusterType(str, Enum):
    CLOUD = "CLOUD"
    REMOTE = "REMOTE"
    ADOPTED = "ADOPTED"
    DOCKER = "DOCKER"


class ClusterLabels(StrEnum):
    GPU_TYPE = "cluster.exalsius.ai/gpu-type"
    WORKLOAD_TYPE = "cluster.exalsius.ai/workload-type"
    TELEMETRY_TYPE = "cluster.exalsius.ai/telemetry-enabled"


class ClusterLabelValuesGPUType(StrEnum):
    NVIDIA = "nvidia"


class ClusterLabelValuesWorkloadType(StrEnum):
    VOLCANO = "volcano"


class ClusterLabelValuesTelemetryType(StrEnum):
    ENABLED = "true"
    DISABLED = "false"


class ClustersBaseRequestDTO(BaseRequestDTO):
    api: ClustersApi = Field(..., description="The API client")


class ClustersListRequestDTO(ClustersBaseRequestDTO):
    status: Optional[str] = Field(..., description="The status of the cluster")


class ClustersGetRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster to get")


class ClustersDeleteRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster to delete")


class ClustersCreateRequestDTO(ClustersBaseRequestDTO):
    name: str = Field(description="The name of the cluster")
    cluster_type: ClusterType = Field(
        description="The type of the cluster. - `CLOUD`: Cloud cluster, consisting of cloud instances - `REMOTE`: Remote cluster, consisting of self-managed nodes - `ADOPTED`: Adopted cluster, consisting of an already existing kubernetes cluster - `DOCKER`: Docker cluster, consisting of docker containers (for local testing and development) "
    )
    cluster_labels: Optional[Dict[str, str]] = Field(
        default=None,
        description="The labels of the cluster control which services are deployed in the cluster.",
    )
    colony_id: Optional[str] = Field(
        default=None,
        description="The ID of the colony to add the cluster to (optional). If not provided, the cluster will be added to the default colony.",
    )
    k8s_version: Optional[str] = Field(
        default=None, description="The Kubernetes version of the cluster"
    )
    to_be_deleted_at: Optional[datetime.datetime] = Field(
        default=None,
        description="The date and time the cluster will be deleted (optional).",
    )
    control_plane_node_ids: Optional[List[str]] = Field(
        default=None, description="The IDs of the control plane nodes (optional)."
    )
    worker_node_ids: Optional[List[str]] = Field(
        default=None, description="The IDs of the worker nodes (optional)."
    )

    def to_api_model(self) -> ClusterCreateRequest:
        return ClusterCreateRequest(
            name=self.name,
            cluster_type=self.cluster_type,
            cluster_labels=self.cluster_labels,
            colony_id=self.colony_id,
            k8s_version=self.k8s_version,
            to_be_deleted_at=self.to_be_deleted_at,
            control_plane_node_ids=self.control_plane_node_ids,
            worker_node_ids=self.worker_node_ids,
        )


class ClustersDeployRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster to deploy")


class ClustersServicesRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(
        ..., description="The ID of the cluster to get services for"
    )


class ClustersNodesRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster to get nodes for")


class ClustersResourcesRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(
        ..., description="The ID of the cluster to get resources for"
    )


class NodesToAddDTO(BaseModel):
    node_id: str = Field(..., description="The ID of the node to add")
    node_role: str = Field(..., description="The role of the node to add")


class ClustersAddNodeRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster to add nodes to")
    nodes_to_add: List[NodesToAddDTO] = Field(
        ..., description="The nodes to add to the cluster"
    )

    def to_api_model(self) -> ClusterAddNodeRequest:
        return ClusterAddNodeRequest(
            nodes_to_add=[
                ClusterNodeToAdd(
                    node_id=node.node_id,
                    node_role=node.node_role,
                )
                for node in self.nodes_to_add
            ]
        )


class ListCloudCredentialsRequestDTO(BaseRequestDTO):
    api: ManagementApi = Field(..., description="The API client")


class ClustersDownloadKubeConfigRequestDTO(ClustersBaseRequestDTO):
    cluster_id: str = Field(
        ..., description="The ID of the cluster to download the kube config for"
    )


class ClusterNodeDTO(BaseNode):
    role: str = Field(..., description="The role of the node")
