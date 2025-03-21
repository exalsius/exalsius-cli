import threading
from typing import Optional, Tuple

import pandas as pd
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
from exalsius.utils.cloud_utils import get_aws_ubuntu_image_ami
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
    aws_enabled: bool,
    docker_enabled: bool,
    job_name: str,
    instance_type: str,
    parallelism: int,
    region: str,
    ami_id: Optional[str] = None,
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
        aws_enabled=aws_enabled,
        docker_enabled=docker_enabled,
        ami_id=ami_id,
    )
    return rendered_template


def process_job_manifest(path: str) -> Tuple[dict, Optional[str]]:
    """Process and validate the job manifest."""
    try:
        job_manifest = _read_yaml(path)
        target_colony = job_manifest.get("spec", {}).get("targetColony")
        if target_colony:
            return job_manifest, target_colony

        return job_manifest, None
    except Exception as e:
        return None, f"Error reading manifest: {str(e)}"


def create_job_with_existing_colony(
    console: Console, path: str, target_colony: str
) -> bool:
    """Create a job when target colony is already specified."""
    try:
        create_custom_object_from_yaml_file(path)
        console.print("[success]Job created successfully![/success]")
        console.print("[info]You can check the status with: exalsius jobs list[/info]")
        return True
    except Exception as e:
        console.print(f"[error]Error creating job: {e}[/error]")
        return False


def get_instance_options(
    console: Console,
    gpu_types: list[str],
    parallelism: int,
) -> Optional[pd.DataFrame]:
    """Get and process available instance options."""
    enabled_clouds = _list_enabled_clouds()
    console.print(f"Enabled clouds: {enabled_clouds}", style="custom")

    all_instances = {}
    for gpu in gpu_types:
        result = sdk.stream_and_get(
            sdk.list_accelerators(
                gpus_only=True,
                name_filter=gpu,
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
    return processed_data


def display_options_and_get_choice(
    console: Console,
    data_df: pd.DataFrame,
    top_n: int,
    gpu_types: list[str],
) -> Optional[pd.Series]:
    """Display options and get user choice."""
    if data_df is None:
        return None

    if top_n:
        data_df = data_df.head(top_n)
    data_df.insert(0, "id", range(1, 1 + len(data_df)))

    table = create_rich_table(
        data_df,
        f"Top {top_n} cheapest options for {gpu_types} in enabled clouds:",
        id_column=True,
    )
    console.print(table)

    choice = console.input(
        "[custom]Please select an option by entering its ID: [/custom]"
    )
    return data_df.loc[data_df["id"] == int(choice)].iloc[0]


def create_colony_if_needed(
    console: Console,
    cloud: str,
    instance_type: str,
    region: str,
    parallelism: int,
    job_name: str,
) -> bool:
    """Create colony if needed based on selected configuration."""
    if cloud == "Kubernetes":
        console.print("[info]Using existing Kubernetes cluster[/info]")
        return True

    if cloud == "AWS":
        ami_id = get_aws_ubuntu_image_ami(region)
        if not ami_id:
            console.print(
                f"[error]No AMI ID found for Ubuntu 24.04 in region {region}[/error]"
            )
            return False

    colony_template = _render_colony_template(
        aws_enabled=(cloud == "AWS"),
        docker_enabled=False,
        job_name=job_name,
        instance_type=instance_type,
        parallelism=parallelism,
        region=region,
        ami_id=ami_id,
    )

    try:
        create_custom_object_from_yaml(colony_template)
        colony_name = f"{job_name}-colony"
        _wait_for_colony_to_be_ready(colony_name, "default")
        console.print(
            f"[success]Created colony {colony_name} for job {job_name}[/success]"
        )
        return True
    except Exception as e:
        console.print(f"[error]Failed to create colony: {e}[/error]")
        return False


@app.command("submit")
def submit_job(
    path: str = typer.Argument(..., help="Path to the YAML manifest file"),
    top_n: Optional[int] = typer.Option(
        5, "--top", help="Number of top options to show"
    ),
):
    """Submit a training job."""
    console = Console(theme=custom_theme)

    # Process manifest
    job_manifest, target_colony = process_job_manifest(path)
    if not job_manifest:
        console.print(f"[error]{target_colony}[/error]")
        raise typer.Exit(1)

    # Handle existing colony case
    if target_colony:
        console.print(f"[info]Target colony already set to {target_colony}[/info]")
        if create_job_with_existing_colony(console, path, target_colony):
            raise typer.Exit(0)
        raise typer.Exit(1)

    # Extract job details
    job_name = job_manifest.get("metadata", {}).get("name", "unknown")
    gpu_types = job_manifest.get("spec", {}).get("gpuTypes", [])
    parallelism = job_manifest.get("spec", {}).get("parallelism", 1)

    # Get instance options
    with console.status(
        "[custom]Scanning for cheapest options...[/custom]", spinner="bouncingBall"
    ):
        data_df = get_instance_options(console, gpu_types, parallelism)
        if data_df is None:
            console.print(f"[error]No instances found for GPUs {gpu_types}[/error]")
            raise typer.Exit(1)

    # Get user choice
    selected = display_options_and_get_choice(console, data_df, top_n, gpu_types)
    if not selected:
        console.print("[error]Invalid selection[/error]")
        raise typer.Exit(1)

    # Display configuration and get confirmation
    cloud, instance_type, region = selected[["cloud", "instance_type", "region"]]
    console.print("\n[info]Selected configuration:[/info]")
    console.print(f"• Cloud: {cloud}")
    console.print(f"• Instance Type: {instance_type}")
    console.print(f"• Region: {region}")
    console.print(f"• Parallelism: {parallelism}")
    console.print(f"• Total cost: ${selected['price'] * parallelism:.2f}/hour\n")

    if not typer.confirm("Do you want to proceed?"):
        console.print("[info]Operation cancelled[/info]")
        raise typer.Exit(0)

    # Create colony and job
    if not create_colony_if_needed(
        console, cloud, instance_type, region, parallelism, job_name
    ):
        raise typer.Exit(1)

    try:
        create_custom_object_from_yaml(job_manifest)
        console.print("[success]Job created successfully![/success]")
        console.print("[info]You can check the status with: exalsius jobs list[/info]")
    except Exception as e:
        console.print(f"[error]Error creating job: {e}[/error]")
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
