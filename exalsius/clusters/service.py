from pathlib import Path
from typing import Dict, List

from exalsius.clusters.domain import (
    AddNodesParams,
    Cluster,
    ClusterCreateParams,
    ClusterFilterParams,
    ClusterNodeRef,
    ClusterNodeResources,
    NodeToAddParams,
    RemoveNodeParams,
)
from exalsius.clusters.dtos import (
    AddNodesRequestDTO,
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    CreateClusterRequestDTO,
    ListClustersRequestDTO,
)
from exalsius.clusters.gateway.base import ClustersGateway
from exalsius.config import AppConfig
from exalsius.core.base.service import ServiceError
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.core.commons.factories import GatewayFactory
from exalsius.core.commons.gateways.fileio import YamlFileIOGateway
from exalsius.nodes.domain import BaseNode, NodeFilterParams
from exalsius.nodes.gateway.base import NodesGateway


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
        cluster_filter_params: ClusterFilterParams = ClusterFilterParams(
            status=request.status
        )
        clusters: List[Cluster] = self.clusters_gateway.list(cluster_filter_params)
        return [ClusterDTO.from_domain(c) for c in clusters]

    @handle_service_errors("getting cluster")
    def get_cluster(self, cluster_id: str) -> ClusterDTO:
        cluster: Cluster = self.clusters_gateway.get(cluster_id)
        return ClusterDTO.from_domain(cluster)

    @handle_service_errors("deleting cluster")
    def delete_cluster(self, cluster_id: str) -> None:
        self.clusters_gateway.delete(cluster_id)

    @handle_service_errors("creating cluster")
    def create_cluster(self, request: CreateClusterRequestDTO) -> ClusterDTO:
        cluster_create_params: ClusterCreateParams = (
            ClusterCreateParams.from_request_dto(request_dto=request)
        )
        cluster_id: str = self.clusters_gateway.create(cluster_create_params)
        cluster: Cluster = self.clusters_gateway.get(cluster_id)
        return ClusterDTO.from_domain(domain_obj=cluster)

    @handle_service_errors("deploying cluster")
    def deploy_cluster(self, cluster_id: str) -> ClusterDTO:
        self.clusters_gateway.deploy(cluster_id)
        cluster: Cluster = self.clusters_gateway.get(cluster_id)
        return ClusterDTO.from_domain(domain_obj=cluster)

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
                    cluster_id=cluster.id,
                    cluster_name=cluster.name,
                    cluster_node_ref=node_ref,
                    node=nodes_by_id[node_ref.node_id],
                )
            )

        return cluster_nodes_dtos

    @handle_service_errors("adding cluster nodes")
    def add_cluster_nodes(self, request: AddNodesRequestDTO) -> List[ClusterNodeDTO]:
        nodes_to_add: List[NodeToAddParams] = [
            NodeToAddParams(node_id=node_id, node_role=request.node_role)
            for node_id in request.node_ids
        ]
        add_nodes_params: AddNodesParams = AddNodesParams(
            cluster_id=request.cluster_id, nodes_to_add=nodes_to_add
        )
        cluster: Cluster = self.clusters_gateway.get(cluster_id=request.cluster_id)
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
                    cluster_id=request.cluster_id,
                    cluster_name=cluster.name,
                    cluster_node_ref=node_ref,
                    node=nodes_by_id[node_ref.node_id],
                )
            )

        return cluster_nodes_dtos

    @handle_service_errors("removing cluster node")
    def remove_cluster_node(self, remove_node_params: RemoveNodeParams) -> str:
        return self.clusters_gateway.remove_node_from_cluster(remove_node_params)

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
            cluster_node_resources_dtos.append(
                ClusterNodeResourcesDTO.from_base_dto(
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
        kubeconfig_content: str = self.clusters_gateway.get_kubeconfig(
            cluster_id=cluster_id
        )
        self.yaml_fileio_gateway.write_file(
            file_path=kubeconfig_file_path, content=kubeconfig_content
        )


def get_clusters_service(config: AppConfig, access_token: str) -> ClustersService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway()
    nodes_gateway: NodesGateway = gateway_factory.create_nodes_gateway()
    yaml_fileio_gateway: YamlFileIOGateway = (
        gateway_factory.create_yaml_fileio_gateway()
    )
    return ClustersService(
        clusters_gateway=clusters_gateway,
        nodes_gateway=nodes_gateway,
        yaml_fileio_gateway=yaml_fileio_gateway,
    )
