from typing import Any, Dict, List, Optional

import yaml
from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.models.cluster import Cluster as SdkCluster
from exalsius_api_client.models.cluster_add_node_request import ClusterAddNodeRequest
from exalsius_api_client.models.cluster_create_request import ClusterCreateRequest
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_delete_response import ClusterDeleteResponse
from exalsius_api_client.models.cluster_deploy_response import ClusterDeployResponse
from exalsius_api_client.models.cluster_kubeconfig_response import (
    ClusterKubeconfigResponse,
)
from exalsius_api_client.models.cluster_node_remove_response import (
    ClusterNodeRemoveResponse,
)
from exalsius_api_client.models.cluster_node_to_add import ClusterNodeToAdd
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse

from exls.clusters.domain import (
    AddNodesParams,
    Cluster,
    ClusterCreateParams,
    ClusterFilterParams,
    ClusterNodeRef,
    ClusterNodeResources,
    ClusterNodeRole,
    RemoveNodeParams,
    Resources,
)
from exls.core.commons.commands.sdk import (
    ExalsiusSdkCommand,
    UnexpectedSdkCommandResponseError,
)


def _create_cluster_from_sdk_model(sdk_model: SdkCluster) -> Cluster:
    return Cluster(sdk_model=sdk_model)


class BaseClustersSdkCommand[T_Cmd_Params, T_Cmd_Return](
    ExalsiusSdkCommand[ClustersApi, T_Cmd_Params, T_Cmd_Return]
):
    """Base class for all clusters commands. Fixes the generic API type to ClustersApi."""

    pass


class ListClustersSdkCommand(
    BaseClustersSdkCommand[ClusterFilterParams, List[Cluster]]
):
    def _execute_api_call(self, params: Optional[ClusterFilterParams]) -> List[Cluster]:
        assert params is not None
        response: ClustersListResponse = self.api_client.list_clusters(
            cluster_status=params.status.value if params.status else None
        )
        return [
            _create_cluster_from_sdk_model(cluster) for cluster in response.clusters
        ]


class GetClusterSdkCommand(BaseClustersSdkCommand[str, Cluster]):
    def _execute_api_call(self, params: Optional[str]) -> Cluster:
        assert params is not None
        response: ClusterResponse = self.api_client.describe_cluster(cluster_id=params)
        return _create_cluster_from_sdk_model(response.cluster)


class DeleteClusterSdkCommand(BaseClustersSdkCommand[str, str]):
    def _execute_api_call(self, params: Optional[str]) -> str:
        assert params is not None
        response: ClusterDeleteResponse = self.api_client.delete_cluster(
            cluster_id=params
        )
        return response.cluster_id


class CreateClusterSdkCommand(BaseClustersSdkCommand[ClusterCreateParams, str]):
    def _execute_api_call(self, params: Optional[ClusterCreateParams]) -> str:
        assert params is not None
        request = ClusterCreateRequest(
            name=params.name,
            cluster_type=params.cluster_type,
            cluster_labels=params.cluster_labels,
            colony_id=params.colony_id,
            k8s_version=params.k8s_version,
            to_be_deleted_at=params.to_be_deleted_at,
            control_plane_node_ids=params.control_plane_node_ids,
            worker_node_ids=params.worker_node_ids,
        )
        response: ClusterCreateResponse = self.api_client.create_cluster(
            cluster_create_request=request
        )
        return response.cluster_id


class DeployClusterSdkCommand(BaseClustersSdkCommand[str, None]):
    def _execute_api_call(self, params: Optional[str]) -> None:
        assert params is not None
        _: ClusterDeployResponse = self.api_client.deploy_cluster(cluster_id=params)


class GetClusterNodesSdkCommand(BaseClustersSdkCommand[str, List[ClusterNodeRef]]):
    def _execute_api_call(self, params: Optional[str]) -> List[ClusterNodeRef]:
        assert params is not None
        response: ClusterNodesResponse = self.api_client.get_nodes(cluster_id=params)
        cluster_nodes: List[ClusterNodeRef] = [
            ClusterNodeRef(node_id=node_id, role=ClusterNodeRole.WORKER)
            for node_id in response.worker_node_ids
        ] + [
            ClusterNodeRef(node_id=node_id, role=ClusterNodeRole.CONTROL_PLANE)
            for node_id in response.control_plane_node_ids
        ]
        return cluster_nodes


class AddNodesSdkCommand(BaseClustersSdkCommand[AddNodesParams, List[ClusterNodeRef]]):
    def _execute_api_call(
        self, params: Optional[AddNodesParams]
    ) -> List[ClusterNodeRef]:
        assert params is not None
        request = ClusterAddNodeRequest(
            nodes_to_add=[
                ClusterNodeToAdd(node_id=node.node_id, node_role=node.node_role.value)
                for node in params.nodes_to_add
            ]
        )
        response: ClusterNodesResponse = self.api_client.add_nodes(
            cluster_id=params.cluster_id, cluster_add_node_request=request
        )
        cluster_nodes: List[ClusterNodeRef] = [
            ClusterNodeRef(node_id=node_id, role=ClusterNodeRole.WORKER)
            for node_id in response.worker_node_ids
        ] + [
            ClusterNodeRef(node_id=node_id, role=ClusterNodeRole.CONTROL_PLANE)
            for node_id in response.control_plane_node_ids
        ]
        return cluster_nodes


class RemoveNodeSdkCommand(BaseClustersSdkCommand[RemoveNodeParams, str]):
    def _execute_api_call(self, params: Optional[RemoveNodeParams]) -> str:
        assert params is not None
        response: ClusterNodeRemoveResponse = self.api_client.delete_node_from_cluster(
            cluster_id=params.cluster_id, node_id=params.node_id
        )
        return response.node_id


class GetClusterResourcesSdkCommand(
    BaseClustersSdkCommand[str, List[ClusterNodeResources]]
):
    def _execute_api_call(self, params: Optional[str]) -> List[ClusterNodeResources]:
        assert params is not None
        response: ClusterResourcesListResponse = self.api_client.get_cluster_resources(
            cluster_id=params
        )
        cluster_node_resources: List[ClusterNodeResources] = []
        for resource in response.resources:
            if resource.node_id is None:
                raise UnexpectedSdkCommandResponseError(
                    "Node ID is None", self.__class__.__name__
                )
            if resource.available is None:
                raise UnexpectedSdkCommandResponseError(
                    "Available resources are None", self.__class__.__name__
                )
            if resource.occupied is None:
                raise UnexpectedSdkCommandResponseError(
                    "Occupied resources are None", self.__class__.__name__
                )
            cluster_node_resources.append(
                ClusterNodeResources(
                    node_id=resource.node_id,
                    free_resources=Resources(sdk_model=resource.available),
                    occupied_resources=Resources(sdk_model=resource.occupied),
                )
            )

        return cluster_node_resources


class GetKubeconfigSdkCommand(BaseClustersSdkCommand[str, Dict[str, Any]]):
    def _execute_api_call(self, params: Optional[str]) -> Dict[str, Any]:
        assert params is not None
        response: ClusterKubeconfigResponse = self.api_client.get_cluster_kubeconfig(
            cluster_id=params
        )
        if not response.kubeconfig:
            raise UnexpectedSdkCommandResponseError(
                "Kubeconfig response is empty", self.__class__.__name__
            )
        try:
            kubeconfig_content: Dict[str, Any] = yaml.safe_load(response.kubeconfig)
            return kubeconfig_content
        except yaml.YAMLError as e:
            raise UnexpectedSdkCommandResponseError(
                f"Failed to parse kubeconfig: {str(e)}", self.__class__.__name__
            )
