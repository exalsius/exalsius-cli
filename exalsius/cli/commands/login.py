import typer
from rich.console import Console

from exalsius.core.models.login import LoginRequest
from exalsius.core.services.login_service import LoginService
from exalsius.display.login_display import LoginDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def login(ctx: typer.Context):
    """
    Login with your exalsius credentials.
    """
    console = Console(theme=custom_theme)
    service = LoginService()
    display_manager = LoginDisplayManager(console)

    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)

    login_request = LoginRequest(username=username, password=password)
    success, error = service.login(login_request)
    if not success:
        display_manager.display_login_error(error)
        raise typer.Exit(1)
    display_manager.display_login_success()
