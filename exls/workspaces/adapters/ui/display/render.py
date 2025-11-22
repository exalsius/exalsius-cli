from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.shared.adapters.ui.display.render.table import Column, TableRenderContext
from exls.workspaces.adapters.dtos import DeployWorkspaceRequestDTO, WorkspaceDTO

# Check this when implementing config edit feature
# DEFAULT_WORKSPACE_DEPLOYMENT_CONFIG_COMMENTS: Dict[str, str] = {
#     "cluster_id": "The ID of the cluster to deploy the workspace to",
#     "workspace_name": "The name of your workspace",
#     "workspace_template_name": "The name of the workspace template to use",
#     "resources": "The resources you want to allocate to your workspace",
#     "variables": "The variables you want to set for your workspace. Please adjust the values as needed.",
# }

# class TextEditorWorkspaceDeployConfigManager(
#     BaseTextEditor[WorkspaceDeploymentConfigDTO, WorkspaceDeploymentConfigDTO]
# ):
#     """Display manager for workspace deployment configuration in a text editor."""

#     def __init__(
#         self,
#         renderer: YamlSingleItemStringRenderer[
#             WorkspaceDeploymentConfigDTO
#         ] = YamlSingleItemStringRenderer[WorkspaceDeploymentConfigDTO](),
#     ):
#         self._renderer: YamlSingleItemStringRenderer[WorkspaceDeploymentConfigDTO] = (
#             renderer
#         )

#     @property
#     def renderer(self) -> BaseSingleItemRenderer[WorkspaceDeploymentConfigDTO, str]:
#         return self._renderer

#     def display(
#         self,
#         data: WorkspaceDeploymentConfigDTO,
#         comments: Optional[Dict[str, str]] = None,
#     ) -> WorkspaceDeploymentConfigDTO:
#         # TODO: We need to move this deeper into commons
#         yaml_string: str = self._renderer.render(data, comments=comments)
#         edited_yaml_string: Optional[str] = typer.edit(yaml_string)
#         if edited_yaml_string is None:
#             raise UserCancellationException("User cancelled text editor")

#         yaml = YAML(typ="safe")
#         try:
#             data_dict: Dict[str, Any] = yaml.load(edited_yaml_string)  # type: ignore
#             return WorkspaceDeploymentConfigDTO.model_validate(data_dict)
#         except YAMLError as e:
#             raise ExalsiusError(f"Invalid YAML format: {e}") from e
#         except ValidationError as e:
#             raise ExalsiusError(f"Invalid YAML: {str(e)}") from e


DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "workspace_id": TableRenderContext.get_column("ID", no_wrap=True),
    "workspace_name": TableRenderContext.get_column("Name"),
    "workspace_template_name": TableRenderContext.get_column("Template"),
    "workspace_status": TableRenderContext.get_column("Status"),
    "workspace_created_at": TableRenderContext.get_column("Created At"),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
    "workspace_access_information.access_endpoint": TableRenderContext.get_column(
        "Access Endpoint"
    ),
}

DEFAULT_DEPLOY_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "workspace_name": TableRenderContext.get_column("Workspace Name"),
    "workspace_template_name": TableRenderContext.get_column("Template"),
    "cluster_name": TableRenderContext.get_column("Deployed to Cluster"),
    "resources.gpu_count": TableRenderContext.get_column("GPUs"),
    "resources.cpu_cores": TableRenderContext.get_column("CPU Cores"),
    "resources.memory_gb": TableRenderContext.get_column("Memory (GB)"),
    "resources.pvc_storage_gb": TableRenderContext.get_column("Storage (GB)"),
}


DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    WorkspaceDTO: DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP,
    DeployWorkspaceRequestDTO: DEFAULT_DEPLOY_WORKSPACE_DEPLOY_REQUEST_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)
