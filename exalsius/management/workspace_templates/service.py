from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.management.workspace_templates.commands import (
    ListWorkspaceTemplatesCommand,
)
from exalsius.management.workspace_templates.models import (
    ListWorkspaceTemplatesRequestDTO,
)

WORKSPACE_TEMPLATES_API_ERROR_TYPE: str = "WorkspaceTemplatesApiError"


class WorkspaceTemplatesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def list_workspace_templates(self) -> List[WorkspaceTemplate]:
        req: ListWorkspaceTemplatesRequestDTO = ListWorkspaceTemplatesRequestDTO(
            api=ManagementApi(self.api_client)
        )
        command: ListWorkspaceTemplatesCommand = ListWorkspaceTemplatesCommand(
            request=req
        )
        try:
            response: WorkspaceTemplateListResponse = self.execute_command(command)
            return response.workspace_templates
        except ApiException as e:
            raise ServiceError(
                message=f"api error while executing command {command.__class__.__name__}: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=WORKSPACE_TEMPLATES_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=WORKSPACE_TEMPLATES_API_ERROR_TYPE,
            )
