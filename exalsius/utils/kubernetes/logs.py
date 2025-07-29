from typing import Optional

from kubernetes import watch
from rich.console import Console

from exalsius.utils.theme import custom_theme

from .client import KubernetesClient


class LogManager(KubernetesClient):
    """Manages Kubernetes pod log commands."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console(theme=custom_theme)
        self.watch = watch.Watch()

    def stream_pod_logs(
        self,
        pod_name: str,
        namespace: str,
        container: Optional[str] = None,
        color: str = "white",
    ) -> None:
        """
        Stream logs from a single pod using a Watch.

        Args:
            pod_name: Name of the pod
            namespace: Namespace where the pod is located
            container: Optional container name if pod has multiple containers
            color: Color to use for log output
        """
        try:
            for log_line in self.watch.stream(
                self.core_api.read_namespaced_pod_log,
                name=pod_name,
                namespace=namespace,
                follow=True,
                container=container,
                _preload_content=False,
            ):
                self.console.print(f"{pod_name} : {log_line}", style=color)
        except Exception as e:
            self.console.print(
                f"Error streaming logs for pod {pod_name}: {e}", style="red"
            )
