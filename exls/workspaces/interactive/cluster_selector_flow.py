from typing import TYPE_CHECKING, List, Optional

import questionary

from exls.clusters.dtos import ClusterDTO
from exls.workspaces.interactive.base_flow import BaseWorkspaceDeployFlow
from exls.workspaces.interactive.mappers import clusters_to_questionary_choices

if TYPE_CHECKING:
    from exls.workspaces.common.display import ComposingWorkspaceDeployDisplayManager


class WorkspaceClusterSelectorFlow(BaseWorkspaceDeployFlow):
    """Flow for selecting a cluster for workspace deployment."""

    def __init__(
        self,
        clusters: List[ClusterDTO],
        display_manager: "ComposingWorkspaceDeployDisplayManager",
    ):
        super().__init__(display_manager)
        if not clusters:
            raise ValueError(
                "No clusters available. Please deploy a cluster first using 'exls clusters deploy'."
            )
        self._clusters: List[ClusterDTO] = clusters

    def run(self) -> Optional[str]:
        """
        Prompt user to select a cluster.

        Returns:
            cluster_id if selected, None if cancelled
        """
        try:
            # Display clusters
            self._display_manager.display_clusters(self._clusters)

            # Prompt for selection
            cluster_choices: List[questionary.Choice] = clusters_to_questionary_choices(
                self._clusters
            )
            cluster_id = self._display_manager.ask_select_required(
                "Select cluster for workspace deployment:",
                choices=cluster_choices,
                default=cluster_choices[0],
            )

            return str(cluster_id)

        except (KeyboardInterrupt, TypeError):
            return None
