from typing import List, Optional

import typer
from rich.console import Console

from exalsius.core.services.offers_service import OffersService
from exalsius.display.offers_display import OffersDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    List and search foravailable GPU offers from cloud providers.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def parse_clouds(value: Optional[List[str]]) -> Optional[List[str]]:
    if not value:
        return None
    if len(value) == 1 and "," in value[0]:
        return [item.strip() for item in value[0].split(",")]
    return value


@app.command("list")
def list_offers(
    gpu: Optional[str] = typer.Option(
        None, "--gpu", help="Filter GPUs by name, e.g. 'H100'"
    ),
    quantity: Optional[int] = typer.Option(
        None, "--quantity", help="Minimum number of GPUs required"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", help="Filter by specific region"
    ),
    clouds: Optional[List[str]] = typer.Option(
        None,
        "--clouds",
        help="List of clouds to search (multiple flags allowed). If not provided, all enabled clouds will be searched.",
    ),
    all_clouds: Optional[bool] = typer.Option(
        False, "--all-clouds", help="Search all public clouds"
    ),
) -> None:
    """
    List available GPU offers from cloud providers.
    """
    console = Console(theme=custom_theme)
    service = OffersService()
    display_manager = OffersDisplayManager(console)

    with console.status(
        "[bold custom]Fetching offers...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        offers, error = service.list_offers(
            gpu_type=gpu,
            quantity=quantity,
            region=region,
            clouds=parse_clouds(clouds),
            all_clouds=all_clouds,
        )

        if error:
            display_manager.print_error(f"Failed to fetch offers: {error}")
            raise typer.Exit(1)

        if not offers:
            display_manager.print_warning("No offers found matching your criteria.")
            return

        display_manager.display_offers(offers)
