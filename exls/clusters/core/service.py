from pathlib import Path
from typing import List

from exls.clusters.core.domain import (
    AddNodesRequest,
    Cluster,
    ClusterCreateRequest,
    ClusterFilterCriteria,
    ClusterNodeResources,
    ClusterNodeRole,
    NodeRef,
    RemoveNodesRequest,
)
from exls.clusters.core.ports import IClustersGateway
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.adapters.gateway.file.gateways import IFileWriteGateway
from exls.shared.core.service import ServiceError


class ClustersService:
    def __init__(
        self,
        clusters_gateway: IClustersGateway,
        file_write_gateway: IFileWriteGateway[str],
    ):
        self.clusters_gateway: IClustersGateway = clusters_gateway
        self.file_write_gateway: IFileWriteGateway[str] = file_write_gateway

    @handle_service_layer_errors("listing clusters")
    def list_clusters(self, criteria: ClusterFilterCriteria) -> List[Cluster]:
        clusters: List[Cluster] = self.clusters_gateway.list(criteria=criteria)
        return clusters

    @handle_service_layer_errors("getting cluster")
    def get_cluster(self, cluster_id: str) -> Cluster:
        return self.clusters_gateway.get(cluster_id=cluster_id)

    @handle_service_layer_errors("deleting cluster")
    def delete_cluster(self, cluster_id: str) -> None:
        self.clusters_gateway.delete(cluster_id=cluster_id)

    def _create_nodes_to_add(
        self, worker_node_ids: List[str], control_plane_node_ids: List[str]
    ) -> List[NodeRef]:
        nodes_to_add: List[NodeRef] = []
        if worker_node_ids:
            for node_id in worker_node_ids:
                nodes_to_add.append(NodeRef(id=node_id, role=ClusterNodeRole.WORKER))
        if control_plane_node_ids:
            for node_id in control_plane_node_ids:
                nodes_to_add.append(
                    NodeRef(id=node_id, role=ClusterNodeRole.CONTROL_PLANE)
                )
        return nodes_to_add

    @handle_service_layer_errors("deploying cluster")
    def deploy_cluster(self, create_params: ClusterCreateRequest) -> str:
        if (
            not create_params.worker_node_ids
            and not create_params.control_plane_node_ids
        ):
            raise ServiceError(
                message="Cluster creation request must contain at least one worker or control plane node",
            )

        # Step 1: Create the cluster
        cluster_id: str = self.clusters_gateway.create(request=create_params)

        # Step 2: Add the nodes to the cluster
        nodes_to_add: List[NodeRef] = self._create_nodes_to_add(
            worker_node_ids=create_params.worker_node_ids or [],
            control_plane_node_ids=create_params.control_plane_node_ids or [],
        )
        self.clusters_gateway.add_nodes_to_cluster(
            request=AddNodesRequest(cluster_id=cluster_id, nodes_to_add=nodes_to_add)
        )

        # Step 3: Deploy the cluster
        return self.clusters_gateway.deploy(cluster_id)

    @handle_service_layer_errors("getting cluster nodes")
    def get_cluster_nodes(self, cluster_id: str) -> List[NodeRef]:
        return self.clusters_gateway.get_cluster_nodes(cluster_id=cluster_id)

    @handle_service_layer_errors("adding cluster nodes")
    def add_cluster_nodes(self, request: AddNodesRequest) -> List[NodeRef]:
        return self.clusters_gateway.add_nodes_to_cluster(request=request)

    @handle_service_layer_errors("removing nodes from cluster")
    def remove_nodes_from_cluster(self, request: RemoveNodesRequest) -> List[str]:
        removed_node_ids: List[str] = self.clusters_gateway.remove_nodes_from_cluster(
            request=request
        )
        return removed_node_ids

    @handle_service_layer_errors("getting cluster resources")
    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        return self.clusters_gateway.get_cluster_resources(cluster_id=cluster_id)

    @handle_service_layer_errors("importing kubeconfig")
    def import_kubeconfig(
        self,
        cluster_id: str,
        kubeconfig_file_path: str = Path.home().joinpath(".kube", "config").as_posix(),
    ) -> None:
        kubeconfig_content: str = self.clusters_gateway.get_kubeconfig(
            cluster_id=cluster_id
        )
        self.file_write_gateway.write_file(
            file_path=Path(kubeconfig_file_path), content=kubeconfig_content
        )

    @handle_service_layer_errors("getting dashboard url")
    def get_dashboard_url(self, cluster_id: str) -> str:
        return self.clusters_gateway.get_dashboard_url(cluster_id=cluster_id)
