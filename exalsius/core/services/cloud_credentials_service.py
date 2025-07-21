from typing import List, Optional, Tuple

from exalsius_api_client.models.credentials import Credentials

from exalsius.core.operations.cloud_credentials_operations import (
    ListCloudCredentialsOperation,
)
from exalsius.core.services.base import BaseServiceWithAuth


class CloudCredentialsService(BaseServiceWithAuth):
    def list_cloud_credentials(self) -> Tuple[List[Credentials], Optional[str]]:
        return self.execute_operation(ListCloudCredentialsOperation(self.api_client))
