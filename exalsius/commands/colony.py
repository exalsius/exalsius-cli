import typer
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from rich.console import Console
from rich.table import Table

from exalsius.utils.k8s_utils import get_cluster_nodes, get_colony_objects
from exalsius.utils.theme import custom_theme

app = typer.Typer()


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

        # Base64 decode the kubeconfig
        import base64

        decoded_kubeconfig = base64.b64decode(kubeconfig).decode()

        # Write to file
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
