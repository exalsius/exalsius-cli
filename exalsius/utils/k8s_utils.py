from typing import Optional, Tuple

import typer
import yaml
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from requests.exceptions import ConnectionError
from rich.console import Console
from urllib3.exceptions import MaxRetryError

from exalsius.utils.theme import custom_theme


def get_cluster_nodes(cluster_name: str) -> list:
    config.load_kube_config()
    api = client.CustomObjectsApi()

    group = "cluster.x-k8s.io"
    version = "v1beta1"
    plural = "machines"

    response = api.list_cluster_custom_object(
        group=group, version=version, plural=plural
    )
    # only return the nodes where spec.clusterName matches the cluster_name
    nodes = [
        node
        for node in response.get("items", [])
        if node.get("spec", {}).get("clusterName") == cluster_name
    ]
    return nodes


def get_colony_objects() -> Tuple[Optional[list], Optional[str]]:
    """
    Returns a tuple of (colony_list, error_message).
    If successful, error_message will be None.
    If failed, colony_list will be None and error_message will contain the error.
    """
    try:
        config.load_kube_config()
    except Exception as e:
        return None, f"Failed to load kubeconfig: {str(e)}"

    api = client.CustomObjectsApi()
    group = "infra.exalsius.ai"
    version = "v1"
    plural = "colonies"

    try:
        response = api.list_cluster_custom_object(
            group=group, version=version, plural=plural
        )
        return response.get("items", []), None
    except (ConnectionError, MaxRetryError) as e:
        return None, f"Failed to connect to Kubernetes API server: {str(e)}"
    except ApiException as e:
        if e.status == 404:
            return (
                None,
                "Colony Custom Resource Definition (CRD) not found in the cluster",
            )
        return None, f"Kubernetes API error ({e.status}): {e.reason}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def get_ddp_jobs() -> Tuple[Optional[list], Optional[str]]:
    """
    Returns a tuple of (jobs_list, error_message).
    If successful, error_message will be None.
    If failed, jobs_list will be None and error_message will contain the error.
    """
    try:
        config.load_kube_config()
    except Exception as e:
        return None, f"Failed to load kubeconfig: {str(e)}"

    api = client.CustomObjectsApi()
    group = "training.exalsius.ai"
    version = "v1"
    plural = "dilocotorchddps"

    try:
        response = api.list_cluster_custom_object(
            group=group, version=version, plural=plural
        )
        return response.get("items", []), None
    except (ConnectionError, MaxRetryError) as e:
        return None, f"Failed to connect to Kubernetes API server: {str(e)}"
    except ApiException as e:
        if e.status == 404:
            return None, "Torch DDP training job (CRD) not found in the cluster"
        return None, f"Kubernetes API error ({e.status}): {e.reason}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def stream_pod_logs(
    pod_name: str, namespace: str, container: str = None, color: str = "white"
):
    """
    Stream logs from a single pod using a Watch.
    """
    console = Console(theme=custom_theme)
    v1 = client.CoreV1Api()
    w = watch.Watch()
    try:
        # The stream() method yields lines from the pod logs.
        for log_line in w.stream(
            v1.read_namespaced_pod_log,
            name=pod_name,
            namespace=namespace,
            follow=True,
            container=container,
            _preload_content=False,
        ):
            console.print(f"{pod_name} : {log_line.rstrip()}", style=color)
    except Exception as e:
        console.print(f"Error streaming logs for pod {pod_name}: {e}", style="red")


def create_custom_object_from_yaml(manifest_str: str, default_namespace="default"):
    """
    Reads a YAML manifest string (which can contain multiple documents)
    and creates each custom resource using the CustomObjectsApi.
    """
    console = Console()

    try:
        config.load_kube_config()
    except Exception as e:
        console.print(f"[red]Failed to load kubeconfig: {e}[/red]")
        raise typer.Exit(1)

    api_client = client.ApiClient()
    custom_api = client.CustomObjectsApi(api_client)

    api_version = manifest_str["apiVersion"]
    kind = manifest_str["kind"]
    metadata = manifest_str["metadata"]

    if "/" in api_version:
        group, version = api_version.split("/", 1)
    else:
        group = ""
        version = api_version

    plural = kind.lower() + "s"

    # TODO: remove this hack
    if kind == "Colony":
        plural = "colonies"

    namespace = metadata.get("namespace", default_namespace)

    try:
        custom_api.create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            body=manifest_str,
        )
        console.print(
            f"Created {kind} '{metadata.get('name')}' in namespace '{namespace}'."
        )
    except ApiException as e:
        typer.echo(f"Failed to create {kind}: {e}")
        raise typer.Exit(1)


def create_custom_object_from_yaml_file(
    api_client, manifest_path: str, default_namespace="default"
):
    """
    Reads a YAML manifest file (which can contain multiple documents)
    and creates each custom resource using the CustomObjectsApi.
    """
    with open(manifest_path, "r") as f:
        docs = list(yaml.safe_load_all(f))

    for doc in docs:
        if not isinstance(doc, dict):
            continue
        create_custom_object_from_yaml(doc, default_namespace)
