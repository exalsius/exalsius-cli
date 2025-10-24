from time import sleep, time

from exls.auth.domain import (
    DeviceCode,
    Token,
    User,
)
from exls.auth.gateway.base import (
    Auth0AuthenticationParams,
    Auth0FetchDeviceCodeParams,
    Auth0RefreshTokenParams,
    Auth0RevokeTokenParams,
    Auth0ValidateTokenParams,
    AuthGateway,
)
from exls.auth.gateway.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0GetTokenFromDeviceCodeCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    Auth0ValidateTokenCommand,
)
from exls.auth.gateway.dtos import (
    Auth0DeviceCodeResponse,
    Auth0HTTPErrorResponse,
    Auth0TokenResponse,
    Auth0UserResponse,
)
from exls.auth.gateway.errors import (
    Auth0AccessDeniedError,
    Auth0AuthentificationFailed,
    Auth0CommandError,
    Auth0TimeoutError,
    Auth0TokenError,
)
from exls.auth.gateway.mappers import (
    device_code_from_response,
    token_from_response,
    user_from_response,
)
from exls.core.base.commands import CommandError
from exls.core.commons.gateways.commands.http import HTTPCommandError


class Auth0Gateway(AuthGateway):
    def fetch_device_code(self, params: Auth0FetchDeviceCodeParams) -> DeviceCode:
        command: Auth0FetchDeviceCodeCommand = Auth0FetchDeviceCodeCommand(params)
        try:
            response: Auth0DeviceCodeResponse = command.execute()
            return device_code_from_response(response)
        except CommandError as e:
            raise Auth0CommandError(
                message=f"failed to fetch device code: {e.message}",
            ) from e

    def poll_for_authentication(
        self,
        params: Auth0AuthenticationParams,
    ) -> Token:
        command: Auth0GetTokenFromDeviceCodeCommand = (
            Auth0GetTokenFromDeviceCodeCommand(params=params)
        )

        start_time: float = time()
        interval: int = params.poll_interval_seconds

        while True:
            if time() - start_time > params.poll_timeout_seconds:
                raise Auth0TimeoutError(message="Polling for authentication timed out.")

            sleep(interval)

            try:
                response: Auth0TokenResponse = command.execute()
                return token_from_response(
                    client_id=params.client_id, response=response
                )
            except HTTPCommandError as e:
                if e.error_body:
                    auth0_error: Auth0HTTPErrorResponse = (
                        Auth0HTTPErrorResponse.model_validate(e.error_body)
                    )
                    if auth0_error.error == "authorization_pending":
                        continue
                    if auth0_error.error == "slow_down":
                        interval += 1
                        continue
                    if auth0_error.error == "expired_token":
                        raise Auth0TokenError(
                            message=auth0_error.error_description,
                        ) from e
                    if auth0_error.error == "access_denied":
                        raise Auth0AccessDeniedError(
                            message=auth0_error.error_description,
                        ) from e
                raise Auth0AuthentificationFailed(
                    message=f"failed to authenticate: {e.message}"
                ) from e

    def validate_token(self, params: Auth0ValidateTokenParams) -> User:
        command: Auth0ValidateTokenCommand = Auth0ValidateTokenCommand(params=params)
        try:
            response: Auth0UserResponse = command.execute()
            return user_from_response(response=response)
        except CommandError as e:
            raise Auth0CommandError(
                message=f"failed to validate token: {e.message}",
            ) from e

    def refresh_access_token(self, params: Auth0RefreshTokenParams) -> Token:
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(params=params)
        try:
            response: Auth0TokenResponse = command.execute()
            return token_from_response(client_id=params.client_id, response=response)
        except HTTPCommandError as e:
            raise Auth0CommandError(
                message=f"failed to refresh access token: {e.message} - {e.error_body.get('error_description', '') if e.error_body else ''}",
            )
        except CommandError as e:
            raise Auth0CommandError(
                message=f"failed to refresh access token: {e}",
            ) from e

    def revoke_token(self, params: Auth0RevokeTokenParams) -> None:
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(params=params)
        try:
            command.execute()
        except CommandError as e:
            raise Auth0CommandError(
                message=f"failed to revoke token: {e.message}",
            ) from e
