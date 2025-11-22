from time import sleep, time

from exls.auth.adapters.gateway.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0GetTokenFromDeviceCodeCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    Auth0ValidateTokenCommand,
)
from exls.auth.adapters.gateway.dtos import (
    Auth0DeviceCodeResponse,
    Auth0HTTPErrorResponse,
    Auth0TokenResponse,
    Auth0UserResponse,
)
from exls.auth.adapters.gateway.mappers import (
    device_code_from_response,
    token_from_response,
    user_from_response,
)
from exls.auth.core.domain import (
    AuthenticationRequest,
    DeviceCode,
    FetchDeviceCodeRequest,
    RefreshTokenRequest,
    RevokeTokenRequest,
    Token,
    User,
    ValidateTokenRequest,
)
from exls.auth.core.ports import AuthGatewayError, IAuthGateway
from exls.shared.adapters.gateway.http.commands import HTTPCommandError
from exls.shared.core.ports.command import CommandError


class Auth0Gateway(IAuthGateway):
    def fetch_device_code(self, request: FetchDeviceCodeRequest) -> DeviceCode:
        command: Auth0FetchDeviceCodeCommand = Auth0FetchDeviceCodeCommand(request)
        try:
            response: Auth0DeviceCodeResponse = command.execute()
            return device_code_from_response(response)
        except CommandError as e:
            raise AuthGatewayError(
                f"failed to fetch device code: {str(e)}",
            ) from e

    def poll_for_authentication(
        self,
        request: AuthenticationRequest,
    ) -> Token:
        command: Auth0GetTokenFromDeviceCodeCommand = (
            Auth0GetTokenFromDeviceCodeCommand(params=request)
        )

        start_time: float = time()
        interval: int = request.poll_interval_seconds

        while True:
            if time() - start_time > request.poll_timeout_seconds:
                raise AuthGatewayError("Polling for authentication timed out.")

            sleep(interval)

            try:
                response: Auth0TokenResponse = command.execute()
                return token_from_response(
                    client_id=request.client_id, response=response
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
                        raise AuthGatewayError(
                            f"failed to authenticate: {auth0_error.error_description}",
                        ) from e
                    if auth0_error.error == "access_denied":
                        raise AuthGatewayError(
                            f"failed to authenticate: {auth0_error.error_description}",
                        ) from e
                raise AuthGatewayError(f"failed to authenticate: {str(e)}") from e
            except CommandError as e:
                raise AuthGatewayError(f"failed to authenticate: {str(e)}") from e

    def validate_token(self, request: ValidateTokenRequest) -> User:
        command: Auth0ValidateTokenCommand = Auth0ValidateTokenCommand(params=request)
        try:
            response: Auth0UserResponse = command.execute()
            return user_from_response(response=response)
        except CommandError as e:
            raise AuthGatewayError(
                f"failed to validate token: {str(e)}",
            ) from e

    def refresh_access_token(self, request: RefreshTokenRequest) -> Token:
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(params=request)
        try:
            response: Auth0TokenResponse = command.execute()
            return token_from_response(client_id=request.client_id, response=response)
        except HTTPCommandError as e:
            raise AuthGatewayError(
                f"failed to refresh access token: {str(e)} - {e.error_body.get('error_description', '') if e.error_body else ''}",
            )
        except CommandError as e:
            raise AuthGatewayError(
                f"failed to refresh access token: {str(e)}",
            ) from e

    def revoke_token(self, request: RevokeTokenRequest) -> None:
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(params=request)
        try:
            command.execute()
        except CommandError as e:
            raise AuthGatewayError(
                f"failed to revoke token: {str(e)}",
            ) from e
