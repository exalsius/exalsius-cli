import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.cluster_create_response import ClusterCreateResponse
from exalsius_api_client.models.cluster_delete_response import ClusterDeleteResponse
from exalsius_api_client.models.cluster_deploy_response import ClusterDeployResponse
from exalsius_api_client.models.cluster_kubeconfig_response import (
    ClusterKubeconfigResponse,
)
from exalsius_api_client.models.cluster_nodes_response import ClusterNodesResponse
from exalsius_api_client.models.cluster_resources_list_response import (
    ClusterResourcesListResponse,
)
from exalsius_api_client.models.cluster_response import ClusterResponse
from exalsius_api_client.models.clusters_list_response import ClustersListResponse
from exalsius_api_client.models.credentials import Credentials

from exalsius.clusters.commands import (
    AddClusterNodeCommand,
    CreateClusterCommand,
    DeleteClusterCommand,
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
    ClusterLabelValuesWorkloadType,
    ClustersAddNodeRequestDTO,
    ClustersCreateRequestDTO,
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
from exalsius.core.base.service import BaseServiceWithAuth, T
from exalsius.core.commons.commands import SaveFileCommand
from exalsius.core.commons.models import SaveFileRequestDTO, ServiceError


class ClustersService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.clusters_api: ClustersApi = ClustersApi(self.api_client)
        self.management_api: ManagementApi = ManagementApi(self.api_client)

    def _execute_command(self, command: BaseCommand[T]) -> T:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                f"api error while executing command {command.__class__.__name__}. "
                f"Error code: {e.status}, error body: {e.body}"
            )
        except Exception as e:
            raise ServiceError(
                f"unexpected error while executing command {command.__class__.__name__}: {e}"
            )

    def list_clusters(self, status: Optional[str]) -> ClustersListResponse:
        return self.execute_command(
            ListClustersCommand(
                ClustersListRequestDTO(
                    api=self.clusters_api,
                    status=status,
                )
            )
        )

    def get_cluster(self, cluster_id: str) -> ClusterResponse:
        return self.execute_command(
            GetClusterCommand(
                ClustersGetRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def delete_cluster(self, cluster_id: str) -> ClusterDeleteResponse:
        return self.execute_command(
            DeleteClusterCommand(
                ClustersDeleteRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    # TODO: Revisit this to improve the interface to the CLI
    def create_cluster(
        self,
        name: str,
        cluster_type: ClusterType,
        no_gpu: bool,
        diloco: bool,
        colony_id: Optional[str] = None,
        k8s_version: Optional[str] = None,
        to_be_deleted_at: Optional[datetime.datetime] = None,
        control_plane_node_ids: Optional[List[str]] = None,
        worker_node_ids: Optional[List[str]] = None,
        # service_deployments: Optional[List[ServiceDeploymentDTO]] = None,
    ) -> ClusterCreateResponse:
        cluster_labels: Dict[str, str] = {}
        if not no_gpu:
            cluster_labels[ClusterLabels.GPU_TYPE] = ClusterLabelValuesGPUType.NVIDIA
        if diloco:
            cluster_labels[ClusterLabels.WORKLOAD_TYPE] = (
                ClusterLabelValuesWorkloadType.VOLCANO
            )

        return self.execute_command(
            CreateClusterCommand(
                ClustersCreateRequestDTO(
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
            )
        )

    def deploy_cluster(self, cluster_id: str) -> ClusterDeployResponse:
        return self.execute_command(
            DeployClusterCommand(
                ClustersDeployRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def get_cluster_nodes(self, cluster_id: str) -> ClusterNodesResponse:
        return self.execute_command(
            GetClusterNodesCommand(
                ClustersNodesRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def add_cluster_node(
        self, cluster_id: str, nodes_to_add: List[NodesToAddDTO]
    ) -> ClusterNodesResponse:
        return self.execute_command(
            AddClusterNodeCommand(
                ClustersAddNodeRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                    nodes_to_add=nodes_to_add,
                )
            )
        )

    def get_cluster_resources(self, cluster_id: str) -> ClusterResourcesListResponse:
        return self.execute_command(
            GetClusterResourcesCommand(
                ClustersResourcesRequestDTO(
                    api=self.clusters_api,
                    cluster_id=cluster_id,
                )
            )
        )

    def list_cloud_credentials(self) -> List[Credentials]:
        return self.execute_command(
            ListCloudCredentialsCommand(
                ListCloudCredentialsRequestDTO(
                    api=self.management_api,
                )
            )
        )

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
