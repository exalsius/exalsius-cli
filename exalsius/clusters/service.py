import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cluster import Cluster
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_kubeconfig_response import (
    ClusterKubeconfigResponse,
)
from exalsius_api_client.models.cluster_node_remove_response import (
    ClusterNodeRemoveResponse,
)
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse
from exalsius_api_client.models.credentials import Credentials
from exalsius_api_client.models.node_response import NodeResponse

from exalsius.clusters.commands import (
    AddClusterNodeCommand,
    CreateClusterCommand,
    DeleteClusterCommand,
    DeleteClusterNodeCommand,
    DeployClusterCommand,
    DownloadKubeConfigCommand,
    GetClusterCommand,
    GetClusterNodesCommand,
    GetClusterResourcesCommand,
    ListCloudCredentialsCommand,
    ListClustersCommand,
)
from exalsius.clusters.models import (
    ClusterLabels,
    ClusterLabelValuesGPUType,
    ClusterLabelValuesTelemetryType,
    ClusterLabelValuesWorkloadType,
    ClusterNodeDTO,
    ClusterResourcesDTO,
    ClustersAddNodeRequestDTO,
    ClustersCreateRequestDTO,
    ClustersDeleteNodeRequestDTO,
    ClustersDeleteRequestDTO,
    ClustersDeployRequestDTO,
    ClustersDownloadKubeConfigRequestDTO,
    ClustersGetRequestDTO,
    ClustersListRequestDTO,
    ClustersNodesRequestDTO,
    ClustersResourcesRequestDTO,
    ClusterType,
    ListCloudCredentialsRequestDTO,
    NodesToAddDTO,
)
from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.commands import SaveFileCommand
from exalsius.core.commons.models import SaveFileRequestDTO, ServiceError
from exalsius.nodes.service import NodeService


class ClustersService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.clusters_api: ClustersApi = ClustersApi(self.api_client)
        self.management_api: ManagementApi = ManagementApi(self.api_client)
        self.nodes_service: NodeService = NodeService(config, access_token)

    def _execute_command(self, command: BaseCommand) -> Any:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                f"api error while executing command {command.__class__.__name__}. "
                f"Error code: {e.status}, error body: {e.body}"  # pyright: ignore[reportUnknownMemberType]
            )
        except Exception as e:
            raise ServiceError(
                f"unexpected error while executing command {command.__class__.__name__}: {e}"
            )

    def _get_cluster_nodes_dto_from_response(
        self, cluster_nodes_response: ClusterNodesResponse
    ) -> List[ClusterNodeDTO]:
        nodes: List[ClusterNodeDTO] = []

        if cluster_nodes_response.worker_node_ids:
            for node_id in cluster_nodes_response.worker_node_ids:
                worker_node_response: NodeResponse = self.nodes_service.get_node(
                    node_id
                )
                if worker_node_response.actual_instance:
                    nodes.append(
                        ClusterNodeDTO(
                            role="WORKER",
                            **worker_node_response.actual_instance.to_dict(),
                        )
                    )

        if cluster_nodes_response.control_plane_node_ids:
            for node_id in cluster_nodes_response.control_plane_node_ids:
                control_plane_node_response: NodeResponse = self.nodes_service.get_node(
                    node_id
                )
                if control_plane_node_response.actual_instance:
                    nodes.append(
                        ClusterNodeDTO(
                            role="CONTROL_PLANE",
                            **control_plane_node_response.actual_instance.to_dict(),
                        )
                    )

        return nodes

    def list_clusters(self, status: Optional[str]) -> List[Cluster]:
        request_dto: ClustersListRequestDTO = ClustersListRequestDTO(
            api=self.clusters_api,
            status=status,
        )
        clusters_list_response: ClustersListResponse = self._execute_command(
            ListClustersCommand(request_dto)
        )

        return clusters_list_response.clusters

    def get_cluster(self, cluster_id: str) -> Cluster:
        request_dto: ClustersGetRequestDTO = ClustersGetRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
        )
        cluster_response: ClusterResponse = self._execute_command(
            GetClusterCommand(request_dto)
        )
        return cluster_response.cluster

    def delete_cluster(self, cluster_id: str) -> None:
        request_dto: ClustersDeleteRequestDTO = ClustersDeleteRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
        )
        self._execute_command(DeleteClusterCommand(request_dto))

    # TODO: Revisit this to improve the interface to the CLI
    def create_cluster(
        self,
        name: str,
        cluster_type: ClusterType,
        no_gpu: bool,
        diloco: bool,
        telemetry_enabled: bool,
        colony_id: Optional[str] = None,
        k8s_version: Optional[str] = None,
        to_be_deleted_at: Optional[datetime.datetime] = None,
        control_plane_node_ids: Optional[List[str]] = None,
        worker_node_ids: Optional[List[str]] = None,
    ) -> str:
        cluster_labels: Dict[str, str] = {}
        if not no_gpu:
            cluster_labels[ClusterLabels.GPU_TYPE] = ClusterLabelValuesGPUType.NVIDIA
        if diloco:
            cluster_labels[ClusterLabels.WORKLOAD_TYPE] = (
                ClusterLabelValuesWorkloadType.VOLCANO
            )
        if telemetry_enabled:
            cluster_labels[ClusterLabels.TELEMETRY_TYPE] = (
                ClusterLabelValuesTelemetryType.ENABLED
            )

        request_dto: ClustersCreateRequestDTO = ClustersCreateRequestDTO(
            api=self.clusters_api,
            name=name,
            cluster_type=cluster_type,
            cluster_labels=cluster_labels,
            colony_id=colony_id,
            k8s_version=k8s_version,
            to_be_deleted_at=to_be_deleted_at,
            control_plane_node_ids=control_plane_node_ids,
            worker_node_ids=worker_node_ids,
        )
        cluster_create_response: ClusterCreateResponse = self._execute_command(
            CreateClusterCommand(request_dto)
        )
        return cluster_create_response.cluster_id

    def deploy_cluster(self, cluster_id: str) -> None:
        request_dto: ClustersDeployRequestDTO = ClustersDeployRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
        )
        self._execute_command(DeployClusterCommand(request_dto))

    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeDTO]:
        request_dto: ClustersNodesRequestDTO = ClustersNodesRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
        )
        cluster_nodes_response: ClusterNodesResponse = self._execute_command(
            GetClusterNodesCommand(request_dto)
        )

        return self._get_cluster_nodes_dto_from_response(cluster_nodes_response)

    def add_cluster_node(
        self, cluster_id: str, nodes_to_add: List[NodesToAddDTO]
    ) -> List[ClusterNodeDTO]:
        request_dto: ClustersAddNodeRequestDTO = ClustersAddNodeRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
            nodes_to_add=nodes_to_add,
        )
        cluster_nodes_response: ClusterNodesResponse = self._execute_command(
            AddClusterNodeCommand(request_dto)
        )
        return self._get_cluster_nodes_dto_from_response(cluster_nodes_response)

    def remove_cluster_node(self, cluster_id: str, node_id: str) -> str:
        request_dto: ClustersDeleteNodeRequestDTO = ClustersDeleteNodeRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
            node_id=node_id,
        )
        cluster_node_remove_response: ClusterNodeRemoveResponse = self._execute_command(
            DeleteClusterNodeCommand(request_dto)
        )
        return cluster_node_remove_response.node_id

    def get_available_cluster_resources(
        self, cluster_id: str
    ) -> List[ClusterResourcesDTO]:
        request_dto: ClustersResourcesRequestDTO = ClustersResourcesRequestDTO(
            api=self.clusters_api,
            cluster_id=cluster_id,
        )
        cluster_resources_list_response: ClusterResourcesListResponse = (
            self._execute_command(GetClusterResourcesCommand(request_dto))
        )
        resources: List[ClusterResourcesDTO] = []
        for resource in cluster_resources_list_response.resources:
            if resource.node_id and resource.available:
                resources.append(
                    ClusterResourcesDTO(
                        node_id=resource.node_id,
                        **resource.available.to_dict(),
                    )
                )

        return resources

    def import_kubeconfig(
        self,
        cluster_id: str,
        kubeconfig_path: str = Path.home().joinpath(".kube", "config").as_posix(),
    ) -> None:
        kubeconfig_response: ClusterKubeconfigResponse = self.execute_command(
            DownloadKubeConfigCommand(
                ClustersDownloadKubeConfigRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

        # Check if the parent directory exists and create it if it doesn't
        parent_dir = Path(kubeconfig_path).parent
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ServiceError(
                f"Failed to create the kubeconfig directory '{parent_dir}': {e}"
            )

        # Validate and pretty-print the kubeconfig YAML string from the response
        try:
            kubeconfig_content: str = kubeconfig_response.kubeconfig
            # Validate YAML
            kubeconfig_dict = yaml.safe_load(kubeconfig_content)
            # Pretty-print YAML
            kubeconfig_pretty = yaml.dump(
                kubeconfig_dict, sort_keys=False, default_flow_style=False
            )
        except Exception as e:
            raise ServiceError(
                f"Failed to validate kubeconfig YAML string from response: {e}"
            )

        # Save the kubeconfig to the file
        try:
            SaveFileCommand(
                SaveFileRequestDTO(
                    file_path=kubeconfig_path,
                    content=kubeconfig_pretty,
                )
            ).execute()
        except Exception as e:
            raise ServiceError(f"Failed to save kubeconfig to {kubeconfig_path}: {e}")

    def list_cloud_credentials(self) -> List[Credentials]:
        return self.execute_command(
            ListCloudCredentialsCommand(
                ListCloudCredentialsRequestDTO(
                    api=self.management_api,
                )
            )
        )
