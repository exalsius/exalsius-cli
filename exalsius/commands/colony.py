import base64
from pathlib import Path
from typing import Optional

import typer
import yaml
from jinja2 import Environment, FileSystemLoader
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from rich.console import Console
from rich.table import Table

from exalsius.utils.k8s_utils import (
    create_custom_object_from_yaml,
    create_custom_object_from_yaml_file,
    get_cluster_nodes,
    get_colony_objects,
)
from exalsius.utils.theme import custom_theme

app = typer.Typer()

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


@app.command("list")
def list_colonies():
    """
    Lists all available exalsius colonies along with their status.
    """
    console = Console(theme=custom_theme)
    table = Table(
        title="exalsius Colonies",
        show_header=True,
        header_style="bold",
        border_style="custom",
    )

    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=True)
    table.add_column("Creation Time", style="magenta")
    table.add_column("Ready Clusters", style="green")
    table.add_column("Total Clusters", style="green")
    table.add_column("K8s Version", style="blue")
    table.add_column("Nodes", style="blue")

    colonies, error = get_colony_objects()

    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)

    if not colonies:
        console.print("[yellow]No colonies found.[/yellow]")
        return

    for colony in colonies:
        metadata = colony.get("metadata", {})
        spec = colony.get("spec", {})
        name = metadata.get("name", "unknown")
        status = colony.get("status", {}).get("phase", "unknown")
        creation_time = metadata.get("creationTimestamp", "unknown")
        ready_clusters = colony.get("status", {}).get("readyClusters", 0)
        total_clusters = colony.get("status", {}).get("totalClusters", 0)
        k8s_version = spec.get("k8sVersion", "unknown")

        nodes = {}
        for cluster in colony.get("status", {}).get("clusterRefs", []):
            cluster_name = cluster.get("name")
            nodes[cluster_name] = get_cluster_nodes(cluster_name)

        # Convert nodes dict to printable string
        nodes_str = ""
        for cluster_name, cluster_nodes in nodes.items():
            nodes_str += f"{cluster_name}: {len(cluster_nodes)} nodes\n"
        nodes_str = nodes_str.rstrip("\n")

        table.add_row(
            name,
            str(status),
            creation_time,
            str(ready_clusters),
            str(total_clusters),
            k8s_version,
            nodes_str,
        )
    console.print(table)


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
    """
    Delete a Colony by name.
    """
    try:
        config.load_kube_config()
    except Exception as e:
        typer.echo(f"[red]Failed to load kubeconfig: {e}[/red]")
        raise typer.Exit(1)

    api = client.CustomObjectsApi()

    console = Console()
    try:
        api.delete_namespaced_custom_object(
            group="infra.exalsius.ai",
            version="v1",
            namespace=namespace,
            plural="colonies",
            name=colony_name,
        )
        console.print(
            f"[green]Colony '{colony_name}' in namespace '{namespace}' deleted successfully.[/green]"
        )
    except ApiException as e:
        typer.echo(f"[red]Error deleting colony: {e}[/red]")
        raise typer.Exit(1)


def create_docker_colony(
    name: str,
    nodes: int = 1,
) -> None:
    """Create a Docker-based colony."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("colony-template.yaml.j2")

    values = {
        "name": name,
        "docker_enabled": True,
        "docker_replicas": nodes,
    }

    try:
        rendered = template.render(**values)
        yaml_dict = yaml.safe_load(rendered)
        create_custom_object_from_yaml(yaml_dict)
        return True
    except Exception as e:
        return f"Failed to create Docker colony: {str(e)}"


def create_file_based_colony(
    file_path: Path,
) -> None:
    """Create a colony from a YAML file."""
    try:
        create_custom_object_from_yaml_file(file_path)
        return True
    except FileNotFoundError:
        return f"Colony configuration file not found: {file_path}"
    except Exception as e:
        return f"Failed to create colony from file: {str(e)}"


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
):
    """
    Create a new Colony.

    You can either:\n
    1. Provide a YAML file with the colony configuration using --file\n
    2. Create a Docker-based colony using --docker (optionally with --nodes)
    """
    console = Console(theme=custom_theme)

    if not docker and not file_path:
        console.print(
            "[error]Error: You must provide either --file or --docker[/error]"
        )
        console.print(
            "[info]Run 'exalsius colony create --help' for usage information[/info]"
        )
        raise typer.Exit(1)

    if docker and file_path:
        console.print(
            "[error]Error: Cannot use both --docker and --file together[/error]"
        )
        raise typer.Exit(1)

    result = (
        create_docker_colony(name, nodes or 1)
        if docker
        else create_file_based_colony(file_path)
    )

    if result is True:
        console.print("Colony provisioning started.", style="custom")
        console.print(
            "You can check the status with: exalsius colonies list.", style="custom"
        )
    else:
        console.print(f"[error]{result}[/error]")
        raise typer.Exit(1)


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
    """
    Get kubeconfig for a cluster and save it to a file
    """
    try:
        config.load_kube_config()
    except Exception as e:
        typer.echo(f"[red]Failed to load kubeconfig: {e}[/red]")
        raise typer.Exit(1)

    v1 = client.CoreV1Api()
    console = Console()

    try:
        secret = v1.read_namespaced_secret(f"{colony_name}-kubeconfig", namespace)
        kubeconfig = secret.data["value"]

        decoded_kubeconfig = base64.b64decode(kubeconfig).decode()

        with open(output_file, "w") as f:
            f.write(decoded_kubeconfig)

        console.print(f"[green]Kubeconfig saved to {output_file}[/green]")

    except ApiException as e:
        console.print(f"[red]Error getting kubeconfig: {e}[/red]")
        raise typer.Exit(1)


def _wait_for_colony_to_be_ready(colony_name: str, namespace: str):
    """
    Wait for a colony to be ready by checking its status.
    """
    console = Console(theme=custom_theme)
    custom_api = client.CustomObjectsApi()

    with console.status(
        "[bold custom]Waiting for colony to be ready...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        while True:
            try:
                colony = custom_api.get_namespaced_custom_object(
                    group="infra.exalsius.ai",
                    version="v1",
                    namespace=namespace,
                    plural="colonies",
                    name=colony_name,
                )

                # status = colony.get("status", {}).get("phase")
                status = colony.get("status", {}).get("phase", "unknown")

                if status == "Ready":
                    break
                elif status == "Failed":
                    console.print("[red]Colony failed to become ready[/red]")
                    raise typer.Exit(1)

            except ApiException as e:
                console.print(f"[red]Error checking colony status: {e}[/red]")
                raise typer.Exit(1)

    console.print("[green]Colony is ready![/green]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    List and create exalsius colonies
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
