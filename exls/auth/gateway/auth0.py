from exls.auth.domain import (
    DeviceCode,
    FetchDeviceCodeParams,
    PollForAuthenticationParams,
    RefreshTokenParams,
    RevokeTokenParams,
    Token,
    User,
    ValidateTokenParams,
)
from exls.auth.gateway.base import AuthGateway
from exls.auth.gateway.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0PollForAuthenticationCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    Auth0ValidateTokenCommand,
)
from exls.auth.gateway.dtos import (
    Auth0AuthenticationRequest,
    Auth0DeviceCodeResponse,
    Auth0FetchDeviceCodeRequest,
    Auth0RefreshTokenRequest,
    Auth0RevokeTokenRequest,
    Auth0TokenResponse,
    Auth0UserResponse,
    Auth0ValidateTokenRequest,
)


class Auth0Gateway(AuthGateway):
    def fetch_device_code(self, params: FetchDeviceCodeParams) -> DeviceCode:
        request: Auth0FetchDeviceCodeRequest = Auth0FetchDeviceCodeRequest.from_params(
            params
        )
        command: Auth0FetchDeviceCodeCommand = Auth0FetchDeviceCodeCommand(request)
        response: Auth0DeviceCodeResponse = command.execute()
        return DeviceCode.from_response(response)

    def poll_for_authentication(
        self,
        params: PollForAuthenticationParams,
    ) -> Token:
        request: Auth0AuthenticationRequest = Auth0AuthenticationRequest.from_params(
            params
        )
        command: Auth0PollForAuthenticationCommand = Auth0PollForAuthenticationCommand(
            request
        )
        response: Auth0TokenResponse = command.execute()
        return Token.from_response(client_id=params.client_id, response=response)

    def validate_token(self, params: ValidateTokenParams) -> User:
        request: Auth0ValidateTokenRequest = Auth0ValidateTokenRequest.from_params(
            params=params,
        )
        command: Auth0ValidateTokenCommand = Auth0ValidateTokenCommand(request)
        response: Auth0UserResponse = command.execute()
        return User.from_response(response=response)

    def refresh_access_token(self, params: RefreshTokenParams) -> Token:
        request: Auth0RefreshTokenRequest = Auth0RefreshTokenRequest.from_params(
            params=params,
        )
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(request)
        response: Auth0TokenResponse = command.execute()
        return Token.from_response(client_id=params.client_id, response=response)

    def revoke_token(self, params: RevokeTokenParams) -> None:
        request: Auth0RevokeTokenRequest = Auth0RevokeTokenRequest.from_params(
            params=params,
        )
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(request)
        command.execute()
