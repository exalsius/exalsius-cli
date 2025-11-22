from typing import List, Optional

import questionary
from exls.nodes.dtos import NodeDTO
from exls.shared.adapters.cli.decorators import handle_interactive_flow_errors

from exls.clusters.adapters.dtos import (
    AddNodesRequestDTO,
    AllowedClusterNodeRoleDTO,
    ClusterDTO,
)
from exls.clusters.adapters.ui.display.display import ComposingClusterDisplayManager
from exls.clusters.adapters.ui.interactive.mappers import (
    clusters_to_questionary_choices,
    nodes_to_questionary_choices,
)
from exls.shared.core.ports import UserCancellationException

# TODO: We need a better solution for type-save conversion from questionary.Choice to the actual type.


class ClusterFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive cluster flow."""


class ClusterFlow:
    def __init__(
        self,
        display_manager: ComposingClusterDisplayManager,
    ):
        self._display_manager: ComposingClusterDisplayManager = display_manager

    def _select_cluster(self, clusters: List[ClusterDTO]) -> ClusterDTO:
        cluster_choices: List[questionary.Choice] = clusters_to_questionary_choices(
            clusters
        )
        cluster_choice: questionary.Choice = self._display_manager.ask_select_required(
            "Select cluster:",
            choices=cluster_choices,
            default=cluster_choices[0],
        )
        cluster: Optional[ClusterDTO] = next(
            (cluster for cluster in clusters if cluster.id == str(cluster_choice)),
            None,
        )
        if not cluster:
            raise RuntimeError("Selected cluster not found.")
        return cluster

    def _prompt_node_selection(
        self, nodes: List[NodeDTO], min_choices: int = 1
    ) -> List[NodeDTO]:
        selected_node_choices: List[questionary.Choice] = (
            self._display_manager.ask_checkbox(
                message="Select nodes:",
                choices=nodes_to_questionary_choices(nodes=nodes),
                min_choices=min_choices,
            )
        )
        selected_node_ids: List[str] = [
            str(selected_node) for selected_node in selected_node_choices
        ]
        selected_nodes: List[NodeDTO] = []
        for node_id in selected_node_ids:
            selected_nodes.append(next(node for node in nodes if node.id == node_id))
        if not selected_nodes:
            raise RuntimeError("Selected node not found.")
        return selected_nodes


class ListNodesInteractiveFlow(ClusterFlow):
    def __init__(
        self,
        clusters: List[ClusterDTO],
        display_manager: ComposingClusterDisplayManager,
    ):
        if not clusters:
            raise ValueError(
                "No clusters available to list nodes of. Please create a cluster first."
            )
        super().__init__(display_manager=display_manager)
        self._clusters: List[ClusterDTO] = clusters

    @handle_interactive_flow_errors("listing nodes", ClusterFlowInterruptionException)
    def run(self) -> str:
        self._display_manager.display_info(
            "🚀 List Nodes - Interactive Mode: This will guide you through listing nodes of a cluster",
        )

        self._display_manager.display_info("📋 Step 1: Which cluster to list nodes of?")
        cluster: ClusterDTO = self._select_cluster(clusters=self._clusters)

        return cluster.id


class AddNodesInteractiveFlow(ClusterFlow):
    def __init__(
        self,
        available_clusters: List[ClusterDTO],
        available_nodes: List[NodeDTO],
        display_manager: ComposingClusterDisplayManager,
    ):
        if not available_clusters:
            raise ValueError(
                "No clusters available to add nodes to. Please create a cluster first."
            )
        if not available_nodes:
            raise ValueError(
                "No nodes available to add to a cluster. Please import nodes first."
            )
        super().__init__(display_manager=display_manager)
        self._available_clusters: List[ClusterDTO] = available_clusters
        self._available_nodes: List[NodeDTO] = available_nodes

    @handle_interactive_flow_errors(
        "adding nodes to cluster", ClusterFlowInterruptionException
    )
    def run(self) -> AddNodesRequestDTO:
        self._display_manager.display_info(
            "🚀 Add Nodes to Cluster - Interactive Mode: This will guide you through adding nodes to a cluster",
        )

        self._display_manager.display_info("📋 Step 1: Which cluster to add nodes to?")
        cluster: ClusterDTO = self._select_cluster(clusters=self._available_clusters)
        worker_nodes: List[NodeDTO] = self._prompt_node_selection(
            nodes=self._available_nodes, min_choices=1
        )

        add_nodes_request: AddNodesRequestDTO = AddNodesRequestDTO(
            cluster_id=cluster.id,
            node_ids=[node.id for node in worker_nodes],
            node_role=AllowedClusterNodeRoleDTO.WORKER,
        )

        if not self._display_summary(add_nodes_request):
            raise ClusterFlowInterruptionException(
                "Adding nodes to cluster cancelled by user."
            )
        return add_nodes_request

    def _display_summary(self, add_nodes_request: AddNodesRequestDTO) -> bool:
        self._display_manager.display_add_nodes_request(add_nodes_request)
        return self._display_manager.ask_confirm(
            "Add these nodes to cluster?", default=True
        )
