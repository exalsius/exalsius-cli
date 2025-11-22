import logging

import typer

from exls.auth.adapters.bundle import AuthBundle
from exls.auth.adapters.dtos import DeviceCodeAuthenticationDTO, UserInfoDTO
from exls.auth.adapters.ui.display.display import AuthInteractionManager
from exls.auth.core.domain import AuthSession, DeviceCode
from exls.auth.core.ports import AuthGatewayError, TokenStorageError
from exls.auth.core.service import AuthService, NotLoggedInWarning
from exls.shared.core.service import ServiceError, ServiceWarning

logger = logging.getLogger(__name__)


def login(
    ctx: typer.Context,
):
    """
    Authenticates the user and stores the credentials for future use.

    This command initiates the device code authentication flow. The user is prompted
    to visit a URL and enter a code to authorize the device. The command polls
    for the authentication to complete. Upon success, the tokens are stored
    securely in the system's keyring for subsequent CLI calls.
    """
    bundle = AuthBundle(ctx)
    interaction_manager: AuthInteractionManager = bundle.get_interaction_manager()
    auth_service: AuthService = bundle.get_auth_service(config=bundle.config)

    try:
        device_code: DeviceCode = auth_service.initiate_device_code_login()
        device_code_dto = DeviceCodeAuthenticationDTO.from_domain(device_code)

        interaction_manager.display_auth_poling(dto=device_code_dto)

        auth_session: AuthSession = auth_service.poll_for_authentication(
            device_code_input=device_code
        )

        user_info = UserInfoDTO.from_auth_session(auth_session)

        interaction_manager.display_success_message(
            "Logged in successfully!", output_format=bundle.message_output_format
        )
        interaction_manager.display_data(
            user_info, output_format=bundle.object_output_format
        )
    except ServiceWarning as w:
        interaction_manager.display_info_message(
            str(w), output_format=bundle.message_output_format
        )
        raise typer.Exit(0)
    except (ServiceError, AuthGatewayError, TokenStorageError) as e:
        interaction_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)


def logout(ctx: typer.Context):
    """
    Logs the user out by removing stored credentials.

    This command removes the user's authentication tokens from the system's
    keyring, effectively logging them out of the Exalsius CLI.
    """
    bundle = AuthBundle(ctx)
    interaction_manager: AuthInteractionManager = bundle.get_interaction_manager()
    auth_service: AuthService = bundle.get_auth_service(config=bundle.config)

    try:
        auth_service.logout()
    except NotLoggedInWarning:
        interaction_manager.display_info_message(
            "You are not logged in.", output_format=bundle.message_output_format
        )
        raise typer.Exit(0)
    except ServiceWarning as w:
        interaction_manager.display_info_message(
            str(w), output_format=bundle.message_output_format
        )
        raise typer.Exit(0)
    except (ServiceError, AuthGatewayError, TokenStorageError) as e:
        interaction_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    interaction_manager.display_success_message(
        "Logged out successfully", output_format=bundle.message_output_format
    )
