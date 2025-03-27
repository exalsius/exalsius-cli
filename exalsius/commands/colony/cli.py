import pathlib
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from exalsius.commands.colony.operations import (
    AddNodeOperation,
    CreateColonyOperation,
    DeleteColonyOperation,
    GetKubeconfigOperation,
    ListColoniesOperation,
)
from exalsius.display.colony_display import ColonyDisplayManager
from exalsius.services.colony_service import ColonyService
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.command("list")
def list_colonies():
    """
    List all colonies.
    """
    console = Console(theme=custom_theme)
    service = ColonyService()
    display_manager = ColonyDisplayManager(console)

    with console.status(
        "[bold custom]Fetching colonies...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        colonies, error = service.execute_operation(ListColoniesOperation())
        if error:
            console.print(f"[bold red]Failed to list colonies: {error}[/bold red]")
            raise typer.Exit(1)

        if not colonies:
            console.print("[yellow]No colonies found.[/yellow]")
            return

        display_manager.display_colonies(colonies)


@app.command("delete")
def delete_colony(
    colony_name: str = typer.Argument(..., help="Name of the colony to delete"),
    namespace: str = typer.Option(
        "default",
        "--namespace",
        "-n",
        help="Namespace of the colony (default is 'default')",
    ),
):
    """Delete a Colony by name."""
    console = Console(theme=custom_theme)
    operation = DeleteColonyOperation(colony_name, namespace)
    success, error = operation.execute()

    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)

    if success:
        console.print(
            f"[green]Colony '{colony_name}' in namespace '{namespace}' deleted successfully.[/green]"
        )


@app.command("create")
def create_colony(
    name: str = typer.Option(
        "docker-colony", "--name", "-n", help="Name of the colony"
    ),
    file_path: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Path to YAML file containing colony configuration"
    ),
    docker: bool = typer.Option(False, "--docker", "-d", help="Enable Docker mode"),
    nodes: Optional[int] = typer.Option(
        None, "--nodes", help="Number of Docker nodes (default: 1)"
    ),
    remote: bool = typer.Option(False, "--remote", "-r", help="Enable remote mode"),
    external_address: Optional[str] = typer.Option(
        None,
        "--external-address",
        "-e",
        help="External address of a master node of the exalsius management cluster",
    ),
):
    """
    Create a new Colony.

    You can either:\n
    1. Provide a YAML file with the colony configuration using --file\n
    2. Create a colony with a single cluster to which remote machines can be added using --remote\n
    3. Create a Docker-based colony using --docker (optionally with --nodes)
    """
    console = Console(theme=custom_theme)

    if sum([bool(docker), bool(file_path), bool(remote)]) != 1:
        console.print(
            "[error]Error: You must provide exactly one of --file, --docker, or --remote[/error]"
        )
        raise typer.Exit(1)

    operation = CreateColonyOperation(
        name=name,
        docker=docker,
        remote=remote,
        nodes=nodes or 1,
        file_path=file_path,
        external_address=external_address,
    )

    result = operation.execute()
    # TODO(srnbckr): fix this weird code
    error = result[1] if isinstance(result, tuple) and len(result) > 1 else None

    if error:
        console.print(f"[error]{error}[/error]")
        raise typer.Exit(1)

    console.print("Colony provisioning started.", style="custom")
    console.print(
        "You can check the status with: exalsius colonies list.", style="custom"
    )


@app.command("add-node")
def add_node(
    node_name: str = typer.Argument(..., help="Name of the node"),
    colony_name: str = typer.Option(
        ..., "--colony-name", "-c", help="Name of the colony"
    ),
    cluster_name: str = typer.Option(
        ..., "--cluster-name", "-cl", help="Name of a remote cluster of the colony"
    ),
    ip_address: str = typer.Option(
        ..., "--ip-address", "-i", help="IP address of the node"
    ),
    username: str = typer.Option(..., "--username", "-u", help="Username of the node"),
    ssh_key_path: pathlib.Path = typer.Option(
        ..., "--ssh-key-path", "-k", help="Path to the SSH key"
    ),
):
    """
    Add a node via SSH to a remote colony

    This command will provision a new node via SSH and add it to a remote cluster of a colony.

    Attention: The SSH key will be added to the exalsius management cluster as a secret.
    This currently only works with the "root" user.
    """
    console = Console(theme=custom_theme)
    service = ColonyService()

    node, error = service.execute_operation(
        AddNodeOperation(
            node_name, colony_name, cluster_name, ip_address, username, ssh_key_path
        )
    )

    if error:
        console.print(f"[error]{error}[/error]")
        raise typer.Exit(1)

    if node:
        console.print(
            f"[green]Node '{node_name}' added to colony '{colony_name}' successfully.[/green]"
        )


@app.command("get-kubeconfig")
def get_kubeconfig(
    colony_name: str = typer.Argument(..., help="Name of the colony"),
    output_file: str = typer.Option(
        "kubeconfig.yaml", "--output", "-o", help="Output file path"
    ),
    namespace: str = typer.Option(
        "default",
        "--namespace",
        "-n",
        help="Namespace of the secret (default is 'default')",
    ),
):
    """Get kubeconfig for a cluster and save it to a file"""
    console = Console(theme=custom_theme)
    operation = GetKubeconfigOperation(colony_name, namespace)

    kubeconfig, error = operation.execute()

    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)

    try:
        with open(output_file, "w") as f:
            f.write(kubeconfig)
        console.print(f"[green]Kubeconfig saved to {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving kubeconfig: {e}[/red]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """List and create exalsius colonies"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
