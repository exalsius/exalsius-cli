import threading
from typing import Optional

import typer
import yaml
from jinja2 import Template
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from rich.console import Console
from rich.table import Table
from sky.client import sdk

from exalsius.commands.clouds import _list_enabled_clouds
from exalsius.commands.colony import _wait_for_colony_to_be_ready
from exalsius.utils.cli_utils import create_rich_table
from exalsius.utils.k8s_utils import (
    create_custom_object_from_yaml,
    create_custom_object_from_yaml_file,
    get_ddp_jobs,
    stream_pod_logs,
)
from exalsius.utils.price_utils import _sort_by_cheapest
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.command("list")
def list_jobs():
    """
    Lists all available instances of Pytorch DDP training jobs along with their status.
    """
    console = Console(theme=custom_theme)
    table = Table(title="exalsius Training Jobs", border_style="custom")

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Creation Time", style="green")
    table.add_column("Image", style="blue")
    table.add_column("Script Path", style="blue")
    table.add_column("Parallelism", style="green")
    table.add_column("GPUs per Node", style="green")

    jobs, error = get_ddp_jobs()

    if error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)

    if not jobs:
        console.print("[yellow]No training jobs found.[/yellow]")
        raise typer.Exit(0)

    for job in jobs:
        metadata = job.get("metadata", {})
        name = metadata.get("name", "unknown")
        image = job.get("spec", {}).get("image", "unknown")
        script_path = job.get("spec", {}).get("scriptPath", "unknown")
        parallelism = job.get("spec", {}).get("parallelism", "unknown")
        gpus_per_node = job.get("spec", {}).get("nprocPerNode", "unknown")

        status = job.get("status", {}).get("status", "unknown")
        creation = metadata.get("creationTimestamp", "N/A")
        table.add_row(
            name,
            str(status),
            creation,
            image,
            script_path,
            str(parallelism),
            str(gpus_per_node),
        )

    console.print(table)


def _read_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _render_colony_template(
    job_name: str, instance_type: str, parallelism: int, region: str
) -> str:
    with open("exalsius/templates/colony-template.yaml.j2", "r") as f:
        template_content = f.read()

    colony_name = f"{job_name}-colony"
    cluster_name = f"{colony_name}-c1"
    replicas = parallelism

    template = Template(template_content)
    rendered_template = template.render(
        colony_name=colony_name,
        cluster_name=cluster_name,
        replicas=replicas,
        region=region,
        instance_type=instance_type,
    )
    return yaml.safe_load(rendered_template)


@app.command("submit")
def submit_job(
    path: str = typer.Argument(..., help="Path to the YAML manifest file"),
    top_n: Optional[int] = typer.Option(
        5, "--top", help="Number of top options to show"
    ),
):
    """
    Submit a training job.
    """
    console = Console(theme=custom_theme)

    job_manifest = _read_yaml(path)
    console.print(f"Job manifest loaded from {path}", style="custom")

    job_name: str = job_manifest.get("metadata", {}).get("name", "unknown")
    gpu_types: list[str] = job_manifest.get("spec", {}).get("gpuTypes", [])
    parallelism: int = job_manifest.get("spec", {}).get("parallelism", 1)
    # gpus_per_node: int = job_manifest.get("spec", {}).get("nprocPerNode", 1)

    with console.status(
        "[bold custom]Scanning for cheapest options...[/bold custom]",
        spinner="bouncingBall",
        spinner_style="custom",
    ):
        enabled_clouds = _list_enabled_clouds()
        console.print(f"Enabled clouds: {enabled_clouds}", style="custom")

        all_instances = {}
        for gpu in gpu_types:
            result = sdk.stream_and_get(
                sdk.list_accelerators(
                    gpus_only=True,
                    name_filter=gpu,
                    # TODO: fix the quantity_filter so that at least gpus_per_node are returned
                    # quantity_filter=gpus_per_node,
                    all_regions=True,
                    clouds=enabled_clouds,
                    case_sensitive=False,
                )
            )
            if gpu in result:
                all_instances[gpu] = result[gpu]
            else:
                console.print(f"No instances found for GPU {gpu}", style="custom")

        processed_data = _sort_by_cheapest(all_instances)
        data_df = processed_data

        if data_df is None:
            typer.echo(f"No instances found for GPUs {gpu_types}")
            raise typer.Exit(1)

        # Only keep the the top n entries
        if top_n is not None:
            data_df = data_df.head(top_n)

        # we only scanned for one gpu type
        data_df.insert(0, "id", range(1, 1 + len(data_df)))

    # sort by price
    # console.print(f"The following are the top {top_n} cheapest options for {gpu_types} in the enabled clouds:", style="custom")
    table = create_rich_table(
        data_df,
        f"The following are the top {top_n} cheapest options for {gpu_types} in the enabled clouds:",
        id_column=True,
    )
    console.print(table)

    choice = console.input(
        "[custom]Please select an option by entering its ID: [/custom]"
    )

    # get the row from the dataframe
    row = data_df.loc[data_df["id"] == int(choice)]

    cloud = row["cloud"].values[0]
    instance_type = row["instance_type"].values[0]
    region = row["region"].values[0]

    console.print(
        "This will create a colony and training job with the following configuration:",
        style="custom",
    )
    # hacky workaround to print the correct instance type for Kubernetes clusters
    if cloud == "Kubernetes":
        console.print(
            f"Config: Using {parallelism} instances in the already provisioned {cloud} cloud.\n",
            style="custom",
        )
    else:
        console.print(
            f"Config: {parallelism} {instance_type} instances in {region} using the {cloud} cloud.\n",
            style="custom",
        )
    console.print()
    console.print(
        f"Total price:  $ {row['price'].values[0] * parallelism} / hour", style="custom"
    )

    console.print()
    confirmation = console.input(
        "[custom]Are you sure you want to proceed? (y/n): [/custom]"
    )
    if confirmation != "y":
        console.print("Operation cancelled", style="custom")
        raise typer.Exit(0)

    colony_template = _render_colony_template(
        job_name, instance_type, parallelism, region
    )

    # create_custom_object_from_yaml(client.ApiClient(), colony_template)
    # TODO: fix this hack
    if cloud == "Kubernetes":
        console.print(
            "No colony will be created since the Kubernetes cluster is already provisioned",
            style="custom",
        )
    else:
        create_custom_object_from_yaml(colony_template)
        colony_name = f"{job_name}-colony"
        _wait_for_colony_to_be_ready(colony_name, "default")
        console.print(
            f"Created colony {colony_name} for job {job_name}", style="custom"
        )

    # create the job
    create_custom_object_from_yaml(job_manifest)


def create_job(
    manifest: str = typer.Argument(..., help="Path to the YAML manifest file"),
    namespace: str = typer.Option(
        "default",
        "--namespace",
        "-n",
        help="Namespace of the job (default is 'default')",
    ),
):
    """
    Create a DDPjob by applying the YAML manifest.

    This command reads the provided YAML file (which can contain one or more
    Kubernetes resource definitions) and creates them in the cluster.
    """
    console = Console()

    try:
        config.load_kube_config()
    except Exception as e:
        console.print(f"[red]Failed to load kubeconfig: {e}[/red]")
        raise typer.Exit(1)

    api_client = client.ApiClient()

    try:
        create_custom_object_from_yaml_file(
            api_client, manifest, default_namespace=namespace
        )
        console.print("[green]Job created successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error creating job: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_job(
    job_name: str = typer.Argument(..., help="Name of the job to delete"),
    namespace: str = typer.Option(
        "default",
        "--namespace",
        "-n",
        help="Namespace of the job (default is 'default')",
    ),
):
    """
    Delete a DDP Job by name.
    """
    try:
        config.load_kube_config()
    except Exception as e:
        typer.echo(f"[red]Failed to load kubeconfig: {e}[/red]")
        raise typer.Exit(1)

    # Use CustomObjectsApi instead of BatchV1Api
    api = client.CustomObjectsApi()

    console = Console()
    try:
        api.delete_namespaced_custom_object(
            group="training.exalsius.ai",
            version="v1",
            namespace=namespace,
            plural="ddpjobs",
            name=job_name,
        )
        console.print(
            f"[green]Job '{job_name}' in namespace '{namespace}' deleted successfully.[/green]"
        )
    except ApiException as api_err:
        console.print(f"[red]API error deleting job: {api_err}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error deleting job: {e}[/red]")
        raise typer.Exit(1)


@app.command("stream-logs")
def stream_logs(
    job_name: str = typer.Argument(..., help="Name of the job (without prefix)"),
    namespace: str = typer.Option(
        "default", "--namespace", "-n", help="Namespace to search pods in"
    ),
    container: str = typer.Option(
        None,
        "--container",
        "-c",
        help="Container name (if pod has multiple containers)",
    ),
):
    """
    Stream logs for all pods related to a DDP job.
    """
    try:
        config.load_kube_config()
    except Exception as e:
        typer.echo(f"Error loading kubeconfig: {e}")
        raise typer.Exit(1)

    colors = ["cyan", "magenta", "green", "yellow", "blue", "red", "white"]

    # Build the label selector for the pods
    label_selector = f"job-name=ddp-job-{job_name}"
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

    if not pods.items:
        typer.echo(
            f"No pods found with label '{label_selector}' in namespace '{namespace}'."
        )
        raise typer.Exit(0)

    console = Console()
    console.print(
        f"Streaming logs for {len(pods.items)} pod(s) with label '{label_selector}'..."
    )

    threads = []
    for i, pod in enumerate(pods.items):
        pod_name = pod.metadata.name
        color = colors[i % len(colors)]
        t = threading.Thread(
            target=stream_pod_logs,
            args=(pod_name, namespace, container, color),
            daemon=True,
        )
        threads.append(t)
        t.start()

    # Wait indefinitely on all threads to keep the log streams alive.
    for t in threads:
        t.join()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """
    List and submit training jobs
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
