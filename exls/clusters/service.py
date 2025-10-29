from pathlib import Path
from typing import Any, Dict, List

from exls.clusters.domain import Cluster, ClusterNodeRef, ClusterNodeResources
from exls.clusters.dtos import (
    AddNodesRequestDTO,
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    DeployClusterRequestDTO,
    ListClustersRequestDTO,
    RemoveNodeRequestDTO,
)
from exls.clusters.gateway.base import ClustersGateway
from exls.clusters.gateway.dtos import (
    AddNodesParams,
    ClusterCreateParams,
    ClusterFilterParams,
    RemoveNodeParams,
)
from exls.clusters.mappers import (
    cluster_add_nodes_params_from_add_nodes_request_dto,
    cluster_add_nodes_params_from_deploy_cluster_request_dto,
    cluster_create_params_from_request_dto,
    cluster_list_filter_params_from_request_dto,
)
from exls.config import AppConfig
from exls.core.base.service import ServiceError
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.core.commons.gateways.fileio import YamlFileIOGateway
from exls.nodes.domain import BaseNode
from exls.nodes.gateway.base import NodesGateway
from exls.nodes.gateway.dtos import NodeFilterParams


class ClustersService:
    def __init__(
        self,
        clusters_gateway: ClustersGateway,
        nodes_gateway: NodesGateway,
        yaml_fileio_gateway: YamlFileIOGateway,
    ):
        self.clusters_gateway: ClustersGateway = clusters_gateway
        self.nodes_gateway: NodesGateway = nodes_gateway
        self.yaml_fileio_gateway: YamlFileIOGateway = yaml_fileio_gateway

    @handle_service_errors("listing clusters")
    def list_clusters(self, request: ListClustersRequestDTO) -> List[ClusterDTO]:
        cluster_filter_params: ClusterFilterParams = (
            cluster_list_filter_params_from_request_dto(request_dto=request)
        )
        clusters: List[Cluster] = self.clusters_gateway.list(
            cluster_filter_params=cluster_filter_params
        )
        return [ClusterDTO.from_domain(c) for c in clusters]

    @handle_service_errors("getting cluster")
    def get_cluster(self, cluster_id: str) -> ClusterDTO:
        cluster: Cluster = self.clusters_gateway.get(cluster_id=cluster_id)
        return ClusterDTO.from_domain(cluster)

    @handle_service_errors("deleting cluster")
    def delete_cluster(self, cluster_id: str) -> None:
        self.clusters_gateway.delete(cluster_id=cluster_id)

    @handle_service_errors("deploying cluster")
    def deploy_cluster(self, request: DeployClusterRequestDTO) -> ClusterDTO:
        cluster_create_params: ClusterCreateParams = (
            cluster_create_params_from_request_dto(request_dto=request)
        )
        cluster_id: str = self.clusters_gateway.create(
            cluster_create_params=cluster_create_params
        )

        add_nodes_params: AddNodesParams = (
            cluster_add_nodes_params_from_deploy_cluster_request_dto(
                cluster_id=cluster_id, request_dto=request
            )
        )
        self.clusters_gateway.add_nodes_to_cluster(add_nodes_params=add_nodes_params)

        deployed_cluster_id: str = self.clusters_gateway.deploy(cluster_id)
        deployed_cluster: Cluster = self.clusters_gateway.get(
            cluster_id=deployed_cluster_id
        )

        return ClusterDTO.from_domain(domain_obj=deployed_cluster)

    @handle_service_errors("getting cluster nodes")
    def get_cluster_nodes(self, cluster_id: str) -> List[ClusterNodeDTO]:
        cluster: Cluster = self.clusters_gateway.get(cluster_id=cluster_id)
        cluster_nodes: List[ClusterNodeRef] = self.clusters_gateway.get_cluster_nodes(
            cluster_id=cluster_id
        )

        nodes: List[BaseNode] = self.nodes_gateway.list(
            node_filter_params=NodeFilterParams()
        )
        nodes_by_id: Dict[str, BaseNode] = {node.id: node for node in nodes}

        cluster_nodes_dtos: List[ClusterNodeDTO] = []
        for node_ref in cluster_nodes:
            if node_ref.node_id not in nodes_by_id:
                raise ServiceError(
                    message=f"node with id {node_ref.node_id} not found",
                )
            cluster_nodes_dtos.append(
                ClusterNodeDTO.from_domain(
                    cluster=cluster,
                    cluster_node_ref=node_ref,
                    node=nodes_by_id[node_ref.node_id],
                )
            )

        return cluster_nodes_dtos

    @handle_service_errors("adding cluster nodes")
    def add_cluster_nodes(self, request: AddNodesRequestDTO) -> List[ClusterNodeDTO]:
        cluster: Cluster = self.clusters_gateway.get(cluster_id=request.cluster_id)

        add_nodes_params: AddNodesParams = (
            cluster_add_nodes_params_from_add_nodes_request_dto(request_dto=request)
        )
        cluster_nodes: List[ClusterNodeRef] = (
            self.clusters_gateway.add_nodes_to_cluster(
                add_nodes_params=add_nodes_params
            )
        )

        nodes: List[BaseNode] = self.nodes_gateway.list(
            node_filter_params=NodeFilterParams()
        )
        nodes_by_id: Dict[str, BaseNode] = {node.id: node for node in nodes}

        cluster_nodes_dtos: List[ClusterNodeDTO] = []
        for node_ref in cluster_nodes:
            if node_ref.node_id not in nodes_by_id:
                raise ServiceError(
                    message=f"node with id {node_ref.node_id} not found",
                )
            cluster_nodes_dtos.append(
                ClusterNodeDTO.from_domain(
                    cluster=cluster,
                    cluster_node_ref=node_ref,
                    node=nodes_by_id[node_ref.node_id],
                )
            )

        return cluster_nodes_dtos

    @handle_service_errors("removing cluster node")
    def remove_cluster_node(self, request: RemoveNodeRequestDTO) -> str:
        node_id: str = self.clusters_gateway.remove_node_from_cluster(
            remove_node_params=RemoveNodeParams(
                cluster_id=request.cluster_id,
                node_id=request.node_id,
            )
        )
        return node_id

    @handle_service_errors("getting cluster resources")
    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResourcesDTO]:
        cluster_node_dtos: List[ClusterNodeDTO] = self.get_cluster_nodes(
            cluster_id=cluster_id
        )

        cluster_node_dtos_by_id: Dict[str, ClusterNodeDTO] = {
            dto.node_id: dto for dto in cluster_node_dtos
        }

        cluster_resources: List[ClusterNodeResources] = (
            self.clusters_gateway.get_cluster_resources(cluster_id=cluster_id)
        )

        resources_by_node_id: Dict[str, ClusterNodeResources] = {
            resource.node_id: resource for resource in cluster_resources
        }

        cluster_node_resources_dtos: List[ClusterNodeResourcesDTO] = []
        for node_id in cluster_node_dtos_by_id:
            if node_id not in resources_by_node_id:
                raise ServiceError(
                    message=f"cluster node resources for node {node_id} not found",
                )
            print(resources_by_node_id[node_id])
            cluster_node_resources_dtos.append(
                ClusterNodeResourcesDTO.from_base_dto_and_resources(
                    base_dto=cluster_node_dtos_by_id[node_id],
                    cluster_node_resources=resources_by_node_id[node_id],
                )
            )

        return cluster_node_resources_dtos

    @handle_service_errors("importing kubeconfig")
    def import_kubeconfig(
        self,
        cluster_id: str,
        kubeconfig_file_path: str = Path.home().joinpath(".kube", "config").as_posix(),
    ) -> None:
        kubeconfig_content: Dict[str, Any] = self.clusters_gateway.get_kubeconfig(
            cluster_id=cluster_id
        )
        self.yaml_fileio_gateway.write_file(
            file_path=Path(kubeconfig_file_path), content=kubeconfig_content
        )


def get_clusters_service(config: AppConfig, access_token: str) -> ClustersService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway(
        access_token=access_token,
    )
    nodes_gateway: NodesGateway = gateway_factory.create_nodes_gateway(
        access_token=access_token,
    )
    yaml_fileio_gateway: YamlFileIOGateway = (
        gateway_factory.create_yaml_fileio_gateway()
    )
    return ClustersService(
        clusters_gateway=clusters_gateway,
        nodes_gateway=nodes_gateway,
        yaml_fileio_gateway=yaml_fileio_gateway,
    )
