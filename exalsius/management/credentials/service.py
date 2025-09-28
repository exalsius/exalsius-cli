from typing import List

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.credentials import Credentials
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.management.credentials.commands import ListCredentialsCommand
from exalsius.management.credentials.models import ListCredentialsRequestDTO

CREDENTIALS_API_ERROR_TYPE: str = "CloudCredentialsApiError"


class CredentialsService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)

    def list_credentials(self) -> List[Credentials]:
        try:
            req: ListCredentialsRequestDTO = ListCredentialsRequestDTO(
                api=ManagementApi(self.api_client)
            )
            response: CredentialsListResponse = self.execute_command(
                ListCredentialsCommand(request=req)
            )
            return response.credentials
        except ApiException as e:
            raise ServiceError(
                message=f"api error while fetching cloud credentials: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=CREDENTIALS_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while fetching cloud credentials: {e}",
                error_type=CREDENTIALS_API_ERROR_TYPE,
            )
