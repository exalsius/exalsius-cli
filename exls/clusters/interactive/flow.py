from typing import List

import questionary
from pydantic import StrictStr

from exls.clusters.display import ComposingClusterDisplayManager
from exls.clusters.dtos import (
    AddNodesRequestDTO,
    AllowedClusterNodeRoleDTO,
    AllowedClusterTypesDTO,
    AllowedGpuTypesDTO,
    ClusterDTO,
    DeployClusterRequestDTO,
)
from exls.clusters.interactive.mappers import (
    allowed_gpu_types_to_questionary_choices,
    clusters_to_questionary_choices,
    nodes_to_questionary_choices,
)
from exls.core.base.display import UserCancellationException
from exls.core.commons.decorators import handle_interactive_flow_errors
from exls.core.commons.service import generate_random_name
from exls.nodes.dtos import NodeDTO

# TODO: We need a better solution for type-save conversion from questionary.Choice to the actual type.


class ClusterFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive cluster flow."""


class ClusterInteractiveFlow:
    def __init__(
        self,
        available_nodes: List[NodeDTO],
        display_manager: ComposingClusterDisplayManager,
    ):
        if not available_nodes:
            raise ValueError(
                "No nodes available to create a cluster. Please import nodes first."
            )
        self._display_manager: ComposingClusterDisplayManager = display_manager
        self._available_nodes: List[NodeDTO] = available_nodes

    @handle_interactive_flow_errors(
        "cluster creation", ClusterFlowInterruptionException
    )
    def run(self) -> DeployClusterRequestDTO:
        self._display_manager.display_info(
            "🚀 Cluster Creation - Interactive Mode: This will guide you through creating a new cluster",
        )

        self._display_manager.display_info("📋 Step 1: Cluster Configuration:")
        name: StrictStr = self._display_manager.ask_text(
            "Cluster name:", default=generate_random_name(prefix="exls-cluster")
        )

        gpu_type_choices: List[questionary.Choice] = (
            allowed_gpu_types_to_questionary_choices(default=AllowedGpuTypesDTO.NVIDIA)
        )
        gpu_type_choice: questionary.Choice = self._display_manager.ask_select_required(
            "GPU type:",
            choices=gpu_type_choices,
            default=gpu_type_choices[0],
        )
        gpu_type: AllowedGpuTypesDTO = AllowedGpuTypesDTO(gpu_type_choice.value)

        multinode_training_enabled: bool = self._display_manager.ask_confirm(
            "Enable multinode AI model training?", default=False
        )

        telemetry_enabled: bool = self._display_manager.ask_confirm(
            "Enable telemetry?", default=False
        )

        self._display_manager.display_info("🖥️  Step 2: Node Selection:")
        worker_node_ids: List[StrictStr] = self._prompt_node_selection(
            title="Select worker nodes to add (Space to select, Enter to confirm):",
            nodes=self._available_nodes,
            min_choices=1,
        )
        clusterer_request: DeployClusterRequestDTO = DeployClusterRequestDTO(
            name=name,
            cluster_type=AllowedClusterTypesDTO.REMOTE,
            gpu_type=gpu_type,
            enable_multinode_training=multinode_training_enabled,
            enable_telemetry=telemetry_enabled,
            worker_node_ids=worker_node_ids,
            control_plane_node_ids=[],
        )

        if not self._display_summary(clusterer_request):
            raise ClusterFlowInterruptionException(
                "Cluster creation cancelled by user."
            )
        return clusterer_request

    def _prompt_node_selection(
        self, title: str, nodes: List[NodeDTO], min_choices: int = 1
    ) -> List[StrictStr]:
        selected_node_choices: List[questionary.Choice] = (
            self._display_manager.ask_checkbox(
                message=title,
                choices=nodes_to_questionary_choices(nodes),
                min_choices=min_choices,
            )
        )
        return [str(selected_node) for selected_node in selected_node_choices]

    def _display_summary(self, deploy_cluster_request: DeployClusterRequestDTO) -> bool:
        self._display_manager.display_deploy_cluster_request(deploy_cluster_request)
        return self._display_manager.ask_confirm(
            "Create cluster with these settings?", default=True
        )


class AddNodesInteractiveFlow:
    """Interactive flow for adding nodes to a cluster."""

    def __init__(
        self,
        clusters: List[ClusterDTO],
        available_nodes: List[NodeDTO],
        display_manager: ComposingClusterDisplayManager,
    ):
        if not clusters:
            raise ValueError(
                "No clusters available. Please deploy a cluster first using 'exls clusters deploy'."
            )
        if not available_nodes:
            raise ValueError(
                "No available nodes to add to the cluster. Please import nodes first."
            )
        self._clusters: List[ClusterDTO] = clusters
        self._available_nodes: List[NodeDTO] = available_nodes
        self._display_manager: ComposingClusterDisplayManager = display_manager

    @handle_interactive_flow_errors(
        "adding nodes to cluster", ClusterFlowInterruptionException
    )
    def run(self) -> AddNodesRequestDTO:
        self._display_manager.display_info(
            "🖥️  Add Nodes to Cluster - Interactive Mode: This will guide you through adding nodes to a cluster",
        )

        # Step 1: Cluster Selection
        self._display_manager.display_info("📋 Step 1: Cluster Selection:")
        cluster_id: str = self._select_cluster()

        # Step 2: Node Selection
        self._display_manager.display_info("🖥️  Step 2: Node Selection:")
        node_ids: List[StrictStr] = self._select_nodes()

        # Create request
        add_nodes_request: AddNodesRequestDTO = AddNodesRequestDTO(
            cluster_id=cluster_id,
            node_ids=node_ids,
            node_role=AllowedClusterNodeRoleDTO.WORKER,
        )

        return add_nodes_request

    def _select_cluster(self) -> str:
        """Prompt user to select a cluster."""
        self._display_manager.display_clusters(self._clusters)

        cluster_choices: List[questionary.Choice] = clusters_to_questionary_choices(
            self._clusters
        )
        cluster_id = self._display_manager.ask_select_required(
            "Select cluster to add nodes to:",
            choices=cluster_choices,
            default=cluster_choices[0],
        )
        return str(cluster_id)

    def _select_nodes(self) -> List[StrictStr]:
        """Prompt user to select nodes to add."""
        selected_node_choices: List[questionary.Choice] = (
            self._display_manager.ask_checkbox(
                message="Select nodes to add (Space to select, Enter to confirm):",
                choices=nodes_to_questionary_choices(self._available_nodes),
                min_choices=1,
            )
        )
        return [str(selected_node) for selected_node in selected_node_choices]
