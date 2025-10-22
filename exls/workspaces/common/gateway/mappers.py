from functools import singledispatch

from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest

from exls.workspaces.common.domain import DeployWorkspaceParams


@singledispatch
def to_create_request(params: DeployWorkspaceParams) -> WorkspaceCreateRequest:
    raise NotImplementedError(f"No mapper for type {type(params)}")
