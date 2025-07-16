from typing import List, Optional, Tuple

from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cluster_add_node_request import ClusterAddNodeRequest
from exalsius_api_client.models.cluster_create_request import ClusterCreateRequest
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_delete_response import ClusterDeleteResponse
from exalsius_api_client.models.cluster_deploy_response import ClusterDeployResponse
from exalsius_api_client.models.cluster_node_to_add import ClusterNodeToAdd
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.cluster_services_response import ClusterServicesResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse
from exalsius_api_client.models.error import Error as ExalsiusError

from exalsius.core.operations.base import BaseOperation


class ListClustersOperation(BaseOperation[ClustersListResponse]):
    def __init__(self, api_client: ApiClient, status: Optional[str] = None):
        self.api_client = api_client
        self.status = status

    def execute(self) -> Tuple[Optional[ClustersListResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            clusters_list_response: ClustersListResponse = api_instance.list_clusters(
                cluster_status=self.status
            )
            return clusters_list_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class GetClusterOperation(BaseOperation[ClusterResponse]):
    def __init__(self, api_client: ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[ClusterResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            cluster_response: ClusterResponse = api_instance.describe_cluster(
                self.cluster_id
            )
            return cluster_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class DeleteClusterOperation(BaseOperation[ClusterDeleteResponse]):
    def __init__(self, api_client: ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[ClusterDeleteResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            cluster_delete_response: ClusterDeleteResponse = (
                api_instance.delete_cluster(self.cluster_id)
            )
            return cluster_delete_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class CreateClusterOperation(BaseOperation[ClusterCreateResponse]):
    def __init__(self, api_client: ApiClient, name: str, k8s_version: str):
        self.api_client = api_client
        self.name = name
        self.k8s_version = k8s_version

    def execute(self) -> Tuple[Optional[ClusterCreateResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        cluster_create_request = ClusterCreateRequest(
            name=self.name,
            k8s_version=self.k8s_version,
        )
        try:
            cluster_create_response: ClusterCreateResponse = (
                api_instance.create_cluster(cluster_create_request)
            )
            return cluster_create_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class DeployClusterOperation(BaseOperation[ClusterDeployResponse]):
    def __init__(self, api_client: ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[ClusterDeployResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            cluster_deploy_response: ClusterDeployResponse = (
                api_instance.deploy_cluster(self.cluster_id)
            )
            return cluster_deploy_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class GetClusterServicesOperation(BaseOperation[ClusterServicesResponse]):
    def __init__(self, api_client: ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[ClusterServicesResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            cluster_services_response: ClusterServicesResponse = (
                api_instance.get_cluster_services(self.cluster_id)
            )
            return cluster_services_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class GetClusterNodesOperation(BaseOperation[ClusterNodesResponse]):
    def __init__(self, api_client: ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[ClusterNodesResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            cluster_nodes_response: ClusterNodesResponse = api_instance.get_nodes(
                self.cluster_id
            )
            return cluster_nodes_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class AddClusterNodeOperation(BaseOperation[ClusterNodesResponse]):
    def __init__(
        self,
        api_client: ApiClient,
        cluster_id: str,
        node_ids: List[str],
        node_role: str,
    ):
        self.api_client = api_client
        self.cluster_id = cluster_id
        self.node_ids = node_ids
        self.node_role = node_role

    def execute(self) -> Tuple[Optional[ClusterNodesResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        cluster_add_node_request = ClusterAddNodeRequest(
            nodes_to_add=[
                ClusterNodeToAdd(
                    node_id=node_id,
                    node_role=self.node_role,
                )
                for node_id in self.node_ids
            ]
        )
        try:
            cluster_nodes_response: ClusterNodesResponse = api_instance.add_nodes(
                self.cluster_id, cluster_add_node_request
            )
            return cluster_nodes_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class GetClusterResourcesOperation(BaseOperation[ClusterResourcesListResponse]):
    def __init__(self, api_client: ApiClient, cluster_id: str):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[ClusterResourcesListResponse], Optional[str]]:
        api_instance = ClustersApi(self.api_client)
        try:
            cluster_resources_response: ClusterResourcesListResponse = (
                api_instance.get_cluster_resources(self.cluster_id)
            )
            return cluster_resources_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)
