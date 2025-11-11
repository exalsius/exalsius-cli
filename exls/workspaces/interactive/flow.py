from typing import List

import questionary
from typing_extensions import Optional

from exls.clusters.dtos import ClusterDTO
from exls.core.base.display import UserCancellationException
from exls.core.commons.decorators import handle_interactive_flow_errors
from exls.core.commons.display import non_empty_string_validator
from exls.core.commons.service import generate_random_name
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO
from exls.workspaces.display import ComposingWorkspaceDisplayManager
from exls.workspaces.dtos import DeployWorkspaceRequestDTO
from exls.workspaces.interactive.dtos import (
    WorkspaceDeploymentConfigDTO,
    WorkspaceDeploymentResourcesConfigDTO,
)
from exls.workspaces.interactive.mappers import (
    clusters_to_questionary_choices,
    templates_to_questionary_choices,
    workspace_deployment_config_to_deploy_workspace_request_dto,
)


class WorkspaceFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive workspace flow."""


class WorkspaceInteractiveFlow:
    def __init__(
        self,
        clusters: List[ClusterDTO],
        workspace_templates: List[WorkspaceTemplateDTO],
        display_manager: ComposingWorkspaceDisplayManager,
    ):
        if not clusters:
            raise ValueError(
                "No clusters available to create a workspace. Please deploy a cluster first using 'exls clusters deploy'."
            )
        self._display_manager: ComposingWorkspaceDisplayManager = display_manager
        self._clusters: List[ClusterDTO] = clusters
        self._workspace_templates: List[WorkspaceTemplateDTO] = workspace_templates

    def _select_workspace_template(self) -> WorkspaceTemplateDTO:
        """
        Prompt user to select a workspace template.

        Returns:
            WorkspaceTemplateDTO if selected, None if cancelled
        """
        self._display_manager.display_workspace_templates(self._workspace_templates)

        workspace_template_choices: List[questionary.Choice] = (
            templates_to_questionary_choices(self._workspace_templates)
        )
        workspace_template_name = self._display_manager.ask_select_required(
            "Select workspace template:",
            choices=workspace_template_choices,
            default=workspace_template_choices[0],
        )
        workspace_template: Optional[WorkspaceTemplateDTO] = next(
            (
                template
                for template in self._workspace_templates
                if template.name == str(workspace_template_name)
            ),
            None,
        )
        if not workspace_template:
            raise RuntimeError("Selected workspace template not found.")

        return workspace_template

    def _select_cluster(self) -> ClusterDTO:
        """
        Prompt user to select a cluster.

        Returns:
            ClusterDTO if selected
        """
        self._display_manager.display_clusters(self._clusters)
        cluster_choices: List[questionary.Choice] = clusters_to_questionary_choices(
            self._clusters
        )
        cluster_name = self._display_manager.ask_select_required(
            "Select cluster to deploy the workspace to:",
            choices=cluster_choices,
            default=cluster_choices[0],
        )
        cluster: Optional[ClusterDTO] = next(
            (
                cluster
                for cluster in self._clusters
                if cluster.name == str(cluster_name)
            ),
            None,
        )
        if not cluster:
            raise RuntimeError("Selected cluster not found.")
        return cluster

    @handle_interactive_flow_errors(
        "workspace creation", WorkspaceFlowInterruptionException
    )
    def run(self) -> DeployWorkspaceRequestDTO:
        self._display_manager.display_info(
            "🚀 Workspace Creation - Interactive Mode: This will guide you through creating a new workspace",
        )

        # Step 1: Select workspace you want to deploy
        self._display_manager.display_info("📋 Step 1: Select Workspace to Deploy")

        workspace_template: WorkspaceTemplateDTO = self._select_workspace_template()

        # Step 2: Select cluster you want to deploy the workspace to
        cluster: ClusterDTO = self._select_cluster()

        # Step 3: Configure workspace deployment
        workspace_name: str = self._display_manager.ask_text(
            "Workspace name:",
            default=generate_random_name(prefix="ws"),
            validator=non_empty_string_validator,
        )

        resources: WorkspaceDeploymentResourcesConfigDTO = (
            WorkspaceDeploymentResourcesConfigDTO()
        )

        workspace_deployment_config: WorkspaceDeploymentConfigDTO = (
            WorkspaceDeploymentConfigDTO(
                cluster_id=cluster.id,
                cluster_name=cluster.name,
                workspace_name=workspace_name,
                workspace_template_name=workspace_template.name,
                resources=resources,
                variables=workspace_template.variables,
            )
        )

        workspace_deployment_config_edited: WorkspaceDeploymentConfigDTO = (
            self._display_manager.edit_workspace_deployment_config(
                deployment_config=workspace_deployment_config
            )
        )
        deploy_workspace_request_dto: DeployWorkspaceRequestDTO = (
            workspace_deployment_config_to_deploy_workspace_request_dto(
                deployment_config=workspace_deployment_config_edited
            )
        )
        self._display_manager.display_deploy_workspace_request_dto(
            deploy_workspace_request_dto
        )
        confirmed = self._display_manager.ask_confirm(
            "Deploy workspace with these settings?", default=True
        )
        if not confirmed:
            raise WorkspaceFlowInterruptionException("Deployment cancelled by user.")

        return deploy_workspace_request_dto
