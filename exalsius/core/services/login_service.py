from typing import Optional, Tuple

from exalsius.core.models.login import LoginRequest
from exalsius.core.operations.clusters_operations import ListClustersOperation
from exalsius.core.operations.login_operation import LoginOperation
from exalsius.core.services.base import BaseService


class LoginService(BaseService):
    def login(self, login_request: LoginRequest) -> Tuple[bool, Optional[str]]:
        success, error = self.execute_operation(LoginOperation(login_request))
        if success:
            _, error = self.execute_operation(ListClustersOperation(self.api_client))
            if error:
                return False, error
            return True, None
        return success, error
