import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

from requests import HTTPError

from exalsius.cli.auth.models import (
    Auth0AuthenticationResponse,
    Auth0FetchDeviceCodeRequest,
    Auth0FetchDeviceCodeResponse,
    Auth0PollForAuthenticationRequest,
    Auth0RefreshTokenRequest,
    Auth0ValidateTokenRequest,
    Auth0ValidateTokenResponse,
    LoadTokenFromKeyringRequest,
    LoadTokenFromKeyringResponse,
    StoreTokenOnKeyringRequest,
)
from exalsius.cli.auth.operations import (
    Auth0FetchDeviceCodeOperation,
    Auth0PollForAuthenticationOperation,
    Auth0RefreshTokenOperation,
    Auth0ValidateTokenOperation,
    LoadTokenFromKeyringOperation,
    StoreTokenOnKeyringOperation,
)
from exalsius.cli.config import AppConfig, Auth0Config
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
    ) -> Tuple[Optional[Auth0AuthenticationResponse], Optional[str]]:
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

    def store_token_on_keyring(
        self,
        token: str,
        expires_in: int,
        refresh_token: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        req = StoreTokenOnKeyringRequest(
            client_id=self.config.client_id,
            access_token=token,
            expires_in=expires_in,
            refresh_token=refresh_token,
        )

        return self.execute_operation(StoreTokenOnKeyringOperation(request=req))

    def load_access_token_from_keyring(
        self,
    ) -> Tuple[Optional[LoadTokenFromKeyringResponse], Optional[str]]:
        req = LoadTokenFromKeyringRequest(
            client_id=self.config.client_id,
        )

        resp, error = self.execute_operation(LoadTokenFromKeyringOperation(request=req))
        if error:
            return None, f"error loading token from keyring: {error}"
        if not resp:
            return None, "no token found in keyring"
        return resp, None

    def refresh_access_token(
        self, refresh_token: str
    ) -> Tuple[Optional[Auth0AuthenticationResponse], Optional[str]]:
        req = Auth0RefreshTokenRequest(
            domain=self.config.domain,
            client_id=self.config.client_id,
            refresh_token=refresh_token,
        )

        return self.execute_operation(Auth0RefreshTokenOperation(request=req))

    def acquire_access_token(self) -> Tuple[Optional[str], Optional[str]]:
        load_resp, error = self.load_access_token_from_keyring()
        if error:
            return None, f"could not get token from keyring: {error}"
        if not load_resp:
            return None, "no token found in keyring. Please log in."

        if load_resp.expiry and datetime.now() >= (
            load_resp.expiry
            - timedelta(minutes=self.config.token_expiry_buffer_minutes)
        ):
            if not load_resp.refresh_token:
                return (
                    None,
                    "Session is expired. Please log in again.",
                )

            refresh_resp, error = self.refresh_access_token(load_resp.refresh_token)
            if error:
                return (
                    None,
                    f"failed to refresh access token: {error}. Please log in again.",
                )
            if not refresh_resp:
                return None, "failed to refresh access token. Please log in again."

            _, error = self.store_token_on_keyring(
                token=refresh_resp.access_token,
                expires_in=refresh_resp.expires_in,
                refresh_token=refresh_resp.refresh_token,
            )
            if error:
                pass  # TODO: log error

            return refresh_resp.access_token, None

        return load_resp.access_token, None
