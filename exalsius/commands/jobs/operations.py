import pathlib
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import typer
import yaml
from rich.console import Console

from exalsius.display.job_display import JobDisplayManager
from exalsius.kubernetes.resources import KubernetesClientError, ResourceManager
from exalsius.services.colony_service import ColonyService
from exalsius.utils.theme import custom_theme


class JobOperation(ABC):
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.console = Console(theme=custom_theme)

    @abstractmethod
    def execute(self):
        pass


class ListDDPJobsOperation(JobOperation):
    def execute(self) -> Tuple[Optional[List[dict]], Optional[str]]:
        """
        Execute the list DDP jobs operation.

        Returns:
            Tuple[Optional[List[dict]], Optional[str]]: Tuple containing:
                - List of all DDP jobs if successful, None if failed
                - Error message if failed, None if successful
        """
        return self.resource_manager.get_ddp_jobs()


class GetJobStatusOperation(JobOperation):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def execute(self) -> Tuple[Optional[dict], Optional[str]]:
        """
        Execute the get job status operation.

        Returns:
            Tuple[Optional[dict], Optional[str]]: Tuple containing:
                - The job if found, None if not found or error occurred
                - Error message if failed, None if successful
        """
        try:
            jobs = self.resource_manager.list_custom_objects(
                group="training.exalsius.ai", version="v1", plural="ddpjobs"
            )

            job = next(
                (
                    job
                    for job in jobs.get("items", [])
                    if job.get("metadata", {}).get("name") == self.name
                ),
                None,
            )

            if not job:
                return None, f"Job '{self.name}' not found"

            return job, None

        except KubernetesClientError as e:
            return None, str(e)


class DeleteJobOperation(JobOperation):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__()
        self.name = name
        self.namespace = namespace

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the delete job operation."""
        try:
            self.resource_manager.custom_objects_api.delete_namespaced_custom_object(
                group="training.exalsius.ai",
                version="v1",
                namespace=self.namespace,
                plural="ddpjobs",
                name=self.name,
            )
            return True, None
        except KubernetesClientError as e:
            return False, str(e)


class CreateJobOperation(JobOperation):
    def __init__(
        self,
        job_file_path: pathlib.Path,
        top_n: Optional[int] = 5,
        job_display_manager: JobDisplayManager = None,
        **kwargs,
    ):
        super().__init__()
        self.job_file_path = job_file_path
        self.top_n = top_n
        self.extra_args = kwargs
        # self.suggestion_service = SuggestionService()
        self.colony_service = ColonyService()
        self.job_display_manager = job_display_manager

    def _load_job_manifest(self) -> Tuple[dict, Optional[str]]:
        """Load the job manifest from the file."""
        try:
            with open(self.job_file_path) as f:
                job_manifest: dict = yaml.safe_load(f)
                target_colony = job_manifest.get("spec", {}).get("targetColony", None)
                gpuTypes = job_manifest.get("spec", {}).get("gpuTypes", None)
                return job_manifest, target_colony, gpuTypes
        except Exception:
            return None, None, None

    def _create_job_and_colony(
        self, job_manifest: dict, gpu_types: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """Create a job with a colony."""
        job_name = job_manifest.get("metadata", {}).get("name", "unknown")
        parallelism = job_manifest.get("spec", {}).get("parallelism", 1)

        with self.console.status(
            "[custom]Scanning for cheapest options...[/custom]", spinner="bouncingBall"
        ):
            data_df = self.suggestion_service.get_instance_options(
                self.console, gpu_types, parallelism
            )
            if data_df is None:
                self.console.print(
                    f"[error]No instances found for GPUs {gpu_types}[/error]"
                )
                raise typer.Exit(1)

        selected = self.job_display_manager.display_options_and_get_choice(
            data_df, self.top_n, gpu_types
        )
        if selected is None:
            self.console.print("[error]Invalid selection[/error]")
            raise typer.Exit(1)

        cloud = selected["cloud"]
        instance_type = selected["instance_type"]
        region = selected["region"]
        price = selected["price"]

        self.job_display_manager.display_configuration(
            cloud, instance_type, region, price, parallelism
        )

        # the user has confirmed the configuration and we create the colony
        self.colony_service.create_colony_from_job_submit(
            job_name, cloud, instance_type, region, price, parallelism
        )

        # now we wait until the colony is ready
        self.colony_service.wait_for_colony_to_be_ready(job_name)

        # after the colony is ready, we create the job
        self.resource_manager.create_custom_object_from_dict(job_manifest)

        self.console.print(f"[success]Job '{job_name}' created successfully![/success]")
        return True, None

    def _create_job_with_existing_colony(
        self, job_manifest: dict, target_colony: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Create a job with an existing colony.

        Args:
            job_manifest: The job manifest.
            target_colony: The name of the colony to use.
        Returns:
            Tuple[bool, Optional[str]]: Tuple containing:
                - True if successful, False if failed
        """
        job_name = job_manifest.get("metadata", {}).get("name")
        colony_name = target_colony
        self.console.print(
            f"[info]Creating job '{job_name}' on colony '{colony_name}'...[/info]"
        )
        try:
            self.resource_manager.create_custom_object_from_dict(job_manifest)
            self.console.print(
                f"[success]Job '{job_name}' created successfully![/success]"
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def _create_job_on_mgmt_cluster(self) -> Tuple[bool, Optional[str]]:
        """Create a job on the management cluster."""
        return False, "Management cluster creation not implemented yet"

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the create job operation."""
        job_manifest, target_colony, gpuTypes = self._load_job_manifest()
        if not job_manifest:
            return False, "Failed to load job manifest"

        if target_colony:
            return self._create_job_with_existing_colony(job_manifest, target_colony)

        if gpuTypes:
            return self._create_job_and_colony(job_manifest, gpuTypes)

        return self._create_job_on_mgmt_cluster(job_manifest)


class GetJobLogsOperation(JobOperation):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__()
        self.name = name
        self.namespace = namespace

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the get job logs operation."""
        try:
            # First get the job to find its pods
            job = self.resource_manager.custom_objects_api.get_namespaced_custom_object(
                group="training.exalsius.ai",
                version="v1",
                namespace=self.namespace,
                plural="ddpjobs",
                name=self.name,
            )

            # Get the pod names from the job status
            pods = job.get("status", {}).get("pods", [])
            if not pods:
                return False, "No pods found for this job"

            # Stream logs from each pod
            for pod in pods:
                self.resource_manager.stream_pod_logs(
                    pod_name=pod["name"],
                    namespace=self.namespace,
                    container="training",  # Assuming this is your container name
                )

            return True, None

        except KubernetesClientError as e:
            return False, str(e)
