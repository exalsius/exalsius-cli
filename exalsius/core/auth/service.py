import time
from typing import Optional, Tuple

from requests import HTTPError

from exalsius.cli.config import AppConfig, Auth0Config
from exalsius.core.auth.models import (
    Auth0FetchDeviceCodeRequest,
    Auth0FetchDeviceCodeResponse,
    Auth0PollForAuthenticationRequest,
    Auth0PollForAuthenticationResponse,
    Auth0ValidateTokenRequest,
    Auth0ValidateTokenResponse,
)
from exalsius.core.auth.operations import (
    Auth0FetchDeviceCodeOperation,
    Auth0PollForAuthenticationOperation,
    Auth0ValidateTokenOperation,
)
from exalsius.core.services.base import BaseService


class Auth0Service(BaseService):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config: Auth0Config = config.auth0

    def fetch_device_code(
        self,
    ) -> Tuple[Optional[Auth0FetchDeviceCodeResponse], Optional[str]]:
        req = Auth0FetchDeviceCodeRequest(
            domain=self.config.domain,
            client_id=self.config.client_id,
            audience=self.config.audience,
            scope=self.config.scope,
            algorithms=self.config.algorithms,
        )

        resp, error = self.execute_operation(Auth0FetchDeviceCodeOperation(request=req))

        return resp, error

    def poll_for_authentication(
        self,
        device_code: str,
        interval: int = 5,
    ) -> Tuple[Optional[Auth0PollForAuthenticationResponse], Optional[str]]:
        req: Auth0PollForAuthenticationRequest = Auth0PollForAuthenticationRequest(
            domain=self.config.domain,
            client_id=self.config.client_id,
            device_code=device_code,
            grant_type=self.config.device_code_grant_type,
        )

        op: Auth0PollForAuthenticationOperation = Auth0PollForAuthenticationOperation(
            request=req
        )

        while True:
            time.sleep(interval)
            try:
                resp, error = op.execute()
            except HTTPError as e:
                if "error" in e.response.json():
                    error = e.response.json()["error"]
                    if error == "authorization_pending":
                        continue
                    elif error == "slow_down":
                        interval += 1
                        continue
                if e.response.status_code == 403:
                    return None, "login aborted by user."
                return (
                    None,
                    f"{e.response.json()['error_description'] or e.response.json()}",
                )

            if resp and resp.access_token:
                return resp, None

    def validate_token(
        self, id_token: str
    ) -> Tuple[Optional[Auth0ValidateTokenResponse], Optional[str]]:
        req = Auth0ValidateTokenRequest(
            domain=self.config.domain,
            client_id=self.config.client_id,
            id_token=id_token,
        )

        return self.execute_operation(Auth0ValidateTokenOperation(request=req))
