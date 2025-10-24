from typing import List

from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.management.types.credentials.domain import Credentials
from exls.management.types.credentials.dtos import (
    CredentialsDTO,
    ListCredentialsRequestDTO,
)
from exls.management.types.credentials.gateway.base import CredentialsGateway


class CredentialsService:
    def __init__(
        self,
        credentials_gateway: CredentialsGateway,
    ):
        self.credentials_gateway: CredentialsGateway = credentials_gateway

    @handle_service_errors("listing credentials")
    def list_credentials(
        self, request: ListCredentialsRequestDTO
    ) -> List[CredentialsDTO]:
        credentials: List[Credentials] = self.credentials_gateway.list()
        return [CredentialsDTO.from_domain(c) for c in credentials]


def get_credentials_service(config: AppConfig, access_token: str) -> CredentialsService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    credentials_gateway: CredentialsGateway = (
        gateway_factory.create_credentials_gateway(access_token=access_token)
    )
    return CredentialsService(
        credentials_gateway=credentials_gateway,
    )
