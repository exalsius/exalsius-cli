from typing import Optional

import typer
from rich.console import Console

from exalsius.commands.jobs.operations import (
    CreateJobOperation,
    DeleteJobOperation,
    GetJobLogsOperation,
    ListDDPJobsOperation,
)
from exalsius.display.job_display import JobDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.command("list")
def list_jobs():
    """List all DDP training jobs."""
    console = Console(theme=custom_theme)
    display_manager = JobDisplayManager(console)
    operation = ListDDPJobsOperation()

    with console.status(
        "[bold custom]Fetching jobs...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        jobs, error = operation.execute()

        if error:
            console.print(f"[red]Failed to list jobs: {error}[/red]")
            raise typer.Exit(1)

        if not jobs:
            console.print("[yellow]No jobs found.[/yellow]")
            return

        display_manager.display_jobs(jobs)


@app.command("submit")
def create_job(
    path: str = typer.Argument(..., help="Path to the YAML manifest file"),
    top_n: Optional[int] = typer.Option(
        5, "--top", help="Number of top options to show"
    ),
):
    """Create a new DDP training job."""
    console = Console(theme=custom_theme)
    job_display_manager = JobDisplayManager(console)
    operation = CreateJobOperation(
        job_file_path=path, top_n=top_n, job_display_manager=job_display_manager
    )

    success, error = operation.execute()

    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)

    console.print("[green]Job created successfully.[/green]")


@app.command("delete")
def delete_job(
    name: str = typer.Argument(..., help="Name of the job to delete"),
    namespace: str = typer.Option("default", "--namespace", help="Job namespace"),
):
    """Delete a DDP training job."""
    console = Console(theme=custom_theme)
    operation = DeleteJobOperation(name, namespace)

    with console.status(
        "[bold custom]Deleting job...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        success, error = operation.execute()

        if error:
            console.print(f"[red]{error}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Job '{name}' deleted successfully.[/green]")


@app.command("logs")
def get_job_logs(
    name: str = typer.Argument(..., help="Name of the job"),
    namespace: str = typer.Option("default", "--namespace", help="Job namespace"),
):
    """Get logs from a DDP training job."""
    console = Console(theme=custom_theme)
    operation = GetJobLogsOperation(name, namespace)

    success, error = operation.execute()

    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """Manage DDP training jobs"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
