from time import sleep, time

from exls.auth.adapters.auth0.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0GetTokenFromDeviceCodeCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    ValidateTokenCommand,
)
from exls.auth.adapters.auth0.config import Auth0Config
from exls.auth.adapters.auth0.requests import (
    AuthenticationRequest,
    FetchDeviceCodeRequest,
    RefreshTokenRequest,
    RevokeTokenRequest,
    ValidateTokenRequest,
)
from exls.auth.adapters.auth0.responses import (
    Auth0DeviceCodeResponse,
    Auth0HTTPErrorResponse,
    Auth0TokenResponse,
    ValidatedAuthUserResponse,
)
from exls.auth.core.domain import (
    DeviceCode,
    Token,
    TokenExpiryMetadata,
    User,
)
from exls.auth.core.ports.operations import AuthError, AuthOperations
from exls.shared.adapters.http.commands import HTTPCommandError
from exls.shared.adapters.jwt.commands import DecodeTokenMetadataCommand
from exls.shared.core.ports.command import CommandError


def _user_from_response(response: ValidatedAuthUserResponse) -> User:
    return User(
        email=response.email,
        nickname=response.nickname,
        sub=response.sub,
    )


def _token_from_response(client_id: str, response: Auth0TokenResponse) -> Token:
    return Token(
        client_id=client_id,
        access_token=response.access_token,
        id_token=response.id_token,
        scope=response.scope,
        token_type=response.token_type,
        refresh_token=response.refresh_token,
        expires_in=response.expires_in,
    )


def _device_code_from_response(response: Auth0DeviceCodeResponse) -> DeviceCode:
    return DeviceCode(
        verification_uri=response.verification_uri,
        verification_uri_complete=response.verification_uri_complete,
        user_code=response.user_code,
        device_code=response.device_code,
        expires_in=response.expires_in,
    )


class Auth0Adapter(AuthOperations):
    def __init__(self, config: Auth0Config):
        self._config: Auth0Config = config

    def get_client_id(self) -> str:
        return self._config.client_id

    def fetch_device_code(self) -> DeviceCode:
        request: FetchDeviceCodeRequest = FetchDeviceCodeRequest(
            client_id=self._config.client_id,
            domain=self._config.domain,
            audience=self._config.audience,
            scope=self._config.scope,
            algorithms=self._config.algorithms,
        )
        command: Auth0FetchDeviceCodeCommand = Auth0FetchDeviceCodeCommand(request)
        try:
            response: Auth0DeviceCodeResponse = command.execute()
            return _device_code_from_response(response)
        except CommandError as e:
            # TODO: The objective of the command wrapping is to be able to handle errors more
            #       specifically. The error message should be more specific, adding status,
            #       endpoint, and error description.
            raise AuthError(
                f"failed to fetch device code: {str(e)}",
            ) from e

    def poll_for_authentication(self, device_code: DeviceCode) -> Token:
        request: AuthenticationRequest = AuthenticationRequest(
            client_id=self._config.client_id,
            domain=self._config.domain,
            device_code=device_code.device_code,
            grant_type=self._config.device_code_grant_type,
        )
        command: Auth0GetTokenFromDeviceCodeCommand = (
            Auth0GetTokenFromDeviceCodeCommand(request=request)
        )

        start_time: float = time()
        interval: int = self._config.device_code_poll_interval_seconds

        while True:
            if time() - start_time > self._config.device_code_poll_timeout_seconds:
                raise AuthError("Polling for authentication timed out.")

            sleep(interval)

            try:
                response: Auth0TokenResponse = command.execute()
                return _token_from_response(
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
                        raise AuthError(
                            f"failed to authenticate: {auth0_error.error_description}",
                        ) from e
                    if auth0_error.error == "access_denied":
                        raise AuthError(
                            f"failed to authenticate: {auth0_error.error_description}",
                        ) from e
                raise AuthError(f"failed to authenticate: {str(e)}") from e
            except CommandError as e:
                raise AuthError(f"failed to authenticate: {str(e)}") from e

    def decode_token_expiry_metadata(self, token: str) -> TokenExpiryMetadata:
        command: DecodeTokenMetadataCommand[TokenExpiryMetadata] = (
            DecodeTokenMetadataCommand(
                token=token,
                model=TokenExpiryMetadata,
            )
        )
        try:
            return command.execute()
        except CommandError as e:
            raise AuthError(f"failed to decode token: {str(e)}") from e

    def decode_user_from_token(self, id_token: str) -> User:
        command: DecodeTokenMetadataCommand[User] = DecodeTokenMetadataCommand(
            token=id_token,
            model=User,
        )
        try:
            return command.execute()
        except CommandError as e:
            raise AuthError(f"failed to decode user from token: {str(e)}") from e

    def validate_token(self, id_token: str) -> User:
        request: ValidateTokenRequest = ValidateTokenRequest(
            client_id=self._config.client_id,
            domain=self._config.domain,
            id_token=id_token,
            leeway=self._config.leeway,
        )
        command: ValidateTokenCommand = ValidateTokenCommand(request=request)
        try:
            response: ValidatedAuthUserResponse = command.execute()
            return _user_from_response(response=response)
        except CommandError as e:
            raise AuthError(
                f"failed to validate token: {str(e)}",
            ) from e

    def refresh_access_token(self, refresh_token: str) -> Token:
        request: RefreshTokenRequest = RefreshTokenRequest(
            client_id=self._config.client_id,
            domain=self._config.domain,
            refresh_token=refresh_token,
            scope=" ".join(self._config.scope),
        )
        command: Auth0RefreshTokenCommand = Auth0RefreshTokenCommand(request=request)
        try:
            response: Auth0TokenResponse = command.execute()
            return _token_from_response(client_id=request.client_id, response=response)
        except HTTPCommandError as e:
            raise AuthError(
                f"failed to refresh access token: {str(e)} - {e.error_body.get('error_description', '') if e.error_body else ''}",
            )
        except CommandError as e:
            raise AuthError(
                f"failed to refresh access token: {str(e)}",
            ) from e

    def revoke_token(self, token: str) -> None:
        request: RevokeTokenRequest = RevokeTokenRequest(
            client_id=self._config.client_id,
            domain=self._config.domain,
            token=token,
        )
        command: Auth0RevokeTokenCommand = Auth0RevokeTokenCommand(request=request)
        try:
            command.execute()
        except CommandError as e:
            raise AuthError(
                f"failed to revoke token: {str(e)}",
            ) from e
