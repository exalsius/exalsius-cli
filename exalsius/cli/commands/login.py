import typer
from rich.console import Console

from exalsius.cli import utils
from exalsius.core.models.auth import AuthRequest, Credentials, LogoutRequest, Session
from exalsius.core.services.auth_service import AuthService
from exalsius.display.login_display import LoginDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.command()
def login(
    ctx: typer.Context,
    username: str = typer.Option(None, "--username", "-u"),
    password: str = typer.Option(None, "--password", "-p"),
):
    """
    Login with your exalsius credentials.
    """
    console = Console(theme=custom_theme)
    display_manager = LoginDisplayManager(console)

    auth_service = AuthService()

    if not username or not password:
        # Otherwise, prompt the user for their credentials.
        username = typer.prompt("Username")
        password = typer.prompt("Password", hide_input=True)

    if not username or not password:
        display_manager.print_error("Username and password are required")
        raise typer.Exit(1)

    # Save the credentials to the session file
    auth_request: AuthRequest = AuthRequest(
        credentials=Credentials(username=username, password=password)
    )
    _, error = auth_service.authenticate(auth_request)
    if error:
        display_manager.print_error(f"Authentication failed: {error}")
        raise typer.Exit(1)
    display_manager.display_login_success()


@app.command()
def logout(ctx: typer.Context):
    """
    Logout from the exalsius API.
    """
    session: Session = utils.get_current_session(ctx)
    console = Console(theme=custom_theme)
    display_manager = LoginDisplayManager(console)

    auth_service = AuthService()
    _, error = auth_service.logout(LogoutRequest(session=session))
    if error:
        display_manager.print_error(f"Logout failed: {error}")
        raise typer.Exit(1)
    display_manager.print_success("Successfully logged out.")
