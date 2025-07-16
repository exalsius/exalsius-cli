import logging
from typing import Optional, Tuple

from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.api_client import ApiClient

from exalsius.core.models.auth import (
    AuthRequest,
    AuthResponse,
    LogoutResponse,
    Session,
    ValidateSessionRequest,
    ValidateSessionResponse,
    delete_session,
    save_session,
)
from exalsius.core.operations.base import BaseOperation

logger = logging.getLogger("exalsius.auth")


class BaseAuthOperation(BaseOperation):
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def _test_connection(self) -> bool:
        # TODO: It's a dummy call, change this to a /auth endpoint
        api_instance = OffersApi(self.api_client)
        try:
            _ = api_instance.get_offers()
        except Exception as e:
            logger.debug(f"Failed to connect to the API: {e}")
            return False
        return True


class ValidateSessionOperation(BaseAuthOperation):
    def __init__(
        self, api_client: ApiClient, validate_session_request: ValidateSessionRequest
    ):
        self.api_client = api_client
        self.validate_session_request = validate_session_request

    def execute(self) -> Tuple[Optional[ValidateSessionResponse], Optional[str]]:
        if not self._test_connection():
            return ValidateSessionResponse(valid=False), None
        return ValidateSessionResponse(valid=True), None


class AuthOperation(BaseAuthOperation):
    def __init__(self, auth_request: AuthRequest):
        self.auth_request = auth_request

    def execute(self) -> Tuple[Optional[AuthResponse], Optional[str]]:
        if not self._test_connection():
            return None, "Failed to connect to the API"
        else:
            return (
                AuthResponse(
                    session=Session(credentials=self.auth_request.credentials)
                ),
                None,
            )


class DeleteSessionOperation(BaseOperation):
    def __init__(self, session: Session):
        self.session = session

    def execute(self) -> Tuple[Optional[LogoutResponse], Optional[str]]:
        try:
            delete_session()
            return LogoutResponse(success=True), None
        except Exception as e:
            return None, str(e)


class StoreSessionOperation(BaseOperation):
    def __init__(self, session: Session):
        self.session = session

    def execute(self) -> Tuple[Optional[Session], Optional[str]]:
        try:
            save_session(self.session)
            return self.session, None
        except Exception as e:
            return None, str(e)
