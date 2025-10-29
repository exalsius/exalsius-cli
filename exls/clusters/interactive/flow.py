from typing import List, Optional

import questionary
from pydantic import StrictStr

from exls.clusters.display import ComposingClusterDisplayManager
from exls.clusters.dtos import (
    AllowedClusterTypesDTO,
    AllowedGpuTypesDTO,
    DeployClusterRequestDTO,
)
from exls.clusters.interactive.mappers import (
    allowed_cluster_types_to_questionary_choices,
    allowed_gpu_types_to_questionary_choices,
    nodes_to_questionary_choices,
)
from exls.core.commons.service import generate_random_name
from exls.nodes.dtos import NodeDTO

# TODO: We need a better solution for type-save conversion from questionary.Choice to the actual type.


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

    def run(self) -> Optional[DeployClusterRequestDTO]:
        try:
            self._display_manager.display_info(
                "🚀 Cluster Creation - Interactive Mode: This will guide you through creating a new cluster",
            )

            self._display_manager.display_info("📋 Step 1: Cluster Configuration:")
            name: StrictStr = self._display_manager.ask_text(
                "Cluster name:", default=generate_random_name(prefix="exls-cluster")
            )

            cluster_type_choices: List[questionary.Choice] = (
                allowed_cluster_types_to_questionary_choices(
                    default=AllowedClusterTypesDTO.REMOTE
                )
            )
            cluster_type_choice: questionary.Choice = (
                self._display_manager.ask_select_required(
                    "Cluster type:",
                    choices=cluster_type_choices,
                    default=cluster_type_choices[0],
                )
            )
            cluster_type: AllowedClusterTypesDTO = AllowedClusterTypesDTO(
                cluster_type_choice.value
            )

            gpu_type_choices: List[questionary.Choice] = (
                allowed_gpu_types_to_questionary_choices(
                    default=AllowedGpuTypesDTO.NVIDIA
                )
            )
            gpu_type_choice: questionary.Choice = (
                self._display_manager.ask_select_required(
                    "GPU type:",
                    choices=gpu_type_choices,
                    default=gpu_type_choices[0],
                )
            )
            gpu_type: AllowedGpuTypesDTO = AllowedGpuTypesDTO(gpu_type_choice.value)

            diloco_enabled: bool = self._display_manager.ask_confirm(
                "Enable Diloco/Volcano workload support?", default=False
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
            control_node_ids: List[StrictStr] = self._prompt_node_selection(
                title="Select control plane nodes to add (Space to select, Enter to confirm):",
                nodes=[
                    node
                    for node in self._available_nodes
                    if node.id not in worker_node_ids
                ],
                min_choices=0,
            )
            clusterer_request: DeployClusterRequestDTO = DeployClusterRequestDTO(
                name=name,
                cluster_type=cluster_type,
                gpu_type=gpu_type,
                diloco=diloco_enabled,
                telemetry_enabled=telemetry_enabled,
                worker_node_ids=worker_node_ids,
                control_plane_node_ids=control_node_ids,
            )

            if not self._display_summary(clusterer_request):
                return None

            return clusterer_request
        except (KeyboardInterrupt, TypeError):
            return None

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
