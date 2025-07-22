import typer
from rich.console import Console

from exalsius.cli import utils
from exalsius.cli.state import AppState
from exalsius.core.auth.display import AuthDisplayManager
from exalsius.core.auth.service import Auth0Service
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.command()
def login(
    ctx: typer.Context,
):
    """
    Login with your exalsius credentials.
    """
    app_state: AppState = utils.get_app_state_from_ctx(ctx)

    console: Console = Console(theme=custom_theme)
    display_manager: AuthDisplayManager = AuthDisplayManager(console)

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    resp, error = auth_service.fetch_device_code()
    if error:
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if resp is None:
        display_manager.display_authentication_error("Unexpected error.")
        raise typer.Exit(1)

    display_manager.display_device_code_polling_started(
        verification_uri_complete=resp.verification_uri_complete,
        user_code=resp.user_code,
    )

    try:
        resp, error = auth_service.poll_for_authentication(resp.device_code)
        if error:
            display_manager.display_authentication_error(error)
            raise typer.Exit(1)
        if resp is None:
            display_manager.display_authentication_error("Unexpected error.")
            raise typer.Exit(1)
    except KeyboardInterrupt:
        display_manager.display_device_code_polling_cancelled()
        raise typer.Exit(0)

    resp, error = auth_service.validate_token(resp.id_token)
    if error:
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if not resp:
        display_manager.display_authentication_error("Unexpected error.")
        raise typer.Exit(1)

    display_manager.display_authentication_success(resp.email, resp.sub)


@app.command()
def logout(ctx: typer.Context):
    """
    Logout from the exalsius API.
    """
    pass
