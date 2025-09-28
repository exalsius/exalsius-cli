from exalsius_api_client.models.credentials_list_response import CredentialsListResponse

from exalsius.core.base.commands import BaseCommand
from exalsius.management.credentials.models import ListCredentialsRequestDTO


class ListCredentialsCommand(BaseCommand):
    def __init__(self, request: ListCredentialsRequestDTO):
        self.request: ListCredentialsRequestDTO = request

    def execute(self) -> CredentialsListResponse:
        response: CredentialsListResponse = self.request.api.list_credentials()
        return response
