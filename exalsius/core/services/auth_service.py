from typing import Optional, Tuple

from exalsius.core.models.auth import (
    AuthRequest,
    AuthResponse,
    LogoutRequest,
    LogoutResponse,
    ValidateSessionRequest,
    ValidateSessionResponse,
)
from exalsius.core.operations.auth_operations import (
    AuthOperation,
    DeleteSessionOperation,
    StoreSessionOperation,
    ValidateSessionOperation,
)
from exalsius.core.services.base import BaseService, BaseServiceWithAuth


class SessionService(BaseServiceWithAuth):
    def validate_session(
        self, validate_session_request: ValidateSessionRequest
    ) -> Tuple[Optional[ValidateSessionResponse], Optional[str]]:
        return self.execute_operation(
            ValidateSessionOperation(
                self.api_client,
                validate_session_request=validate_session_request,
            )
        )


class AuthService(BaseService):
    def authenticate(
        self, auth_request: AuthRequest
    ) -> Tuple[Optional[AuthResponse], Optional[str]]:
        auth_response, error = self.execute_operation(
            AuthOperation(auth_request=auth_request)
        )
        if not error and auth_response:
            self.execute_operation(StoreSessionOperation(auth_response.session))
        return auth_response, error

    def logout(
        self, logout_request: LogoutRequest
    ) -> Tuple[Optional[LogoutResponse], Optional[str]]:
        return self.execute_operation(DeleteSessionOperation(logout_request.session))
