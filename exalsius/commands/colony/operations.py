import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

from exalsius.kubernetes.resources import KubernetesClientError, ResourceManager
from exalsius.utils.cloud_utils import get_aws_ubuntu_image_ami
from exalsius.utils.theme import custom_theme

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"


class ColonyOperation(ABC):
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.console = Console(theme=custom_theme)

    @abstractmethod
    def execute(self):
        pass


class ListColoniesOperation(ColonyOperation):
    def execute(self) -> Tuple[Optional[List[dict]], Optional[str]]:
        """
        Execute the list colonies operation.

        Returns:
            Tuple[Optional[List[dict]], Optional[str]]: Tuple containing:
                - List of all colonies as dictionary objects from Kubernetes if successful, None if failed
                - Error message if failed, None if successful
        """
        return self.resource_manager.get_colony_objects()


class DeleteColonyOperation(ColonyOperation):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__()
        self.name = name
        self.namespace = namespace

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the delete colony operation."""
        try:
            self.resource_manager.custom_objects_api.delete_namespaced_custom_object(
                group="infra.exalsius.ai",
                version="v1",
                namespace=self.namespace,
                plural="colonies",
                name=self.name,
            )
            return True, None
        except KubernetesClientError as e:
            return False, str(e)


class CreateColonyFromJobSumitOperation(ColonyOperation):
    def __init__(
        self,
        name: str,
        cloud: str,
        instance_type: str,
        region: str,
        price: float,
        parallelism: int,
    ):
        super().__init__()
        self.name = name
        self.cloud = cloud
        self.instance_type = instance_type
        self.region = region
        self.parallelism = parallelism

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the create colony operation."""
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        if self.cloud == "AWS":
            ami_id = get_aws_ubuntu_image_ami(self.region)
            if not ami_id:
                self.console.print(
                    f"[error]No AMI ID found for Ubuntu 24.04 in region {self.region}[/error]"
                )
                return False

            try:
                template = env.get_template("colony-template.yaml.j2")
                values = {
                    "name": self.name,
                    "aws_enabled": True,
                    "docker_enabled": False,
                    "instance_type": self.instance_type,
                    "region": self.region,
                    "ami_id": ami_id,
                    "parallelism": self.parallelism,
                }
                rendered = template.render(**values)
                yaml_dict = yaml.safe_load(rendered)
                return self.resource_manager.create_custom_object_from_dict(yaml_dict)
            except Exception as e:
                return False, f"Failed to create colony: {str(e)}"
        else:
            return False, "Invalid cloud type"


class CreateColonyOperation(ColonyOperation):
    def __init__(
        self,
        name: str,
        docker: bool = False,
        remote: bool = False,
        nodes: int = 1,
        file_path: Optional[Path] = None,
        external_address: Optional[str] = None,
    ):
        super().__init__()
        self.name = name
        self.docker = docker
        self.remote = remote
        self.nodes = nodes
        self.file_path = file_path
        self.external_address = external_address

    def _create_docker_colony(self) -> Tuple[bool, Optional[str]]:
        """Create a Docker-based colony."""
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        try:
            template = env.get_template("colony-template.yaml.j2")
            values = {
                "name": self.name,
                "docker_enabled": True,
                "docker_replicas": self.nodes,
            }
            rendered = template.render(**values)
            yaml_dict = yaml.safe_load(rendered)
            return self.resource_manager.create_custom_object_from_dict(yaml_dict)
        except Exception as e:
            return False, f"Failed to create Docker colony: {str(e)}"

    def _create_remote_colony(self) -> Tuple[bool, Optional[str]]:
        """Create a remote colony."""
        # Implement remote colony creation logic
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        try:
            template = env.get_template("colony-template.yaml.j2")
            values = {
                "name": self.name,
                "remote_enabled": True,
                "external_address": self.external_address,
            }
            rendered = template.render(**values)
            yaml_dict = yaml.safe_load(rendered)
            return self.resource_manager.create_custom_object_from_dict(yaml_dict)
        except Exception as e:
            return False, f"Failed to create remote colony: {str(e)}"

    def _create_colony_from_file(self) -> Tuple[bool, Optional[str]]:
        """Create a colony from a YAML file."""
        try:
            if not self.file_path:
                return False, "No file path provided"
            with open(self.file_path) as f:
                manifest = yaml.safe_load(f)
            return self.resource_manager.create_custom_object_from_dict(manifest)
        except FileNotFoundError:
            return False, f"Colony configuration file not found: {self.file_path}"
        except Exception as e:
            return False, f"Failed to create colony from file: {str(e)}"

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the create colony operation."""
        if self.docker:
            return self._create_docker_colony()
        elif self.remote:
            return self._create_remote_colony()
        elif self.file_path:
            return self._create_colony_from_file()
        else:
            return False, "Invalid colony creation parameters"


class GetKubeconfigOperation(ColonyOperation):
    def __init__(self, colony_name: str, namespace: str = "default"):
        super().__init__()
        self.colony_name = colony_name
        self.namespace = namespace

    def execute(self) -> Tuple[Optional[str], Optional[str]]:
        """Execute the get kubeconfig operation."""
        try:
            secret = self.resource_manager.core_api.read_namespaced_secret(
                f"{self.colony_name}-kubeconfig", self.namespace
            )
            kubeconfig = secret.data["value"]
            decoded_kubeconfig = base64.b64decode(kubeconfig).decode()
            return decoded_kubeconfig, None
        except KubernetesClientError as e:
            return None, str(e)


class WaitForColonyReadyOperation(ColonyOperation):
    def __init__(self, name: str, namespace: str = "default"):
        super().__init__()
        self.name = name
        self.namespace = namespace

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the wait for colony ready operation."""
        try:
            while True:
                colony = self.resource_manager.custom_objects_api.get_namespaced_custom_object(
                    group="infra.exalsius.ai",
                    version="v1",
                    namespace=self.namespace,
                    plural="colonies",
                    name=self.name,
                )

                status = colony.get("status", {}).get("phase", "unknown")

                if status == "Ready":
                    return True, None
                elif status == "Failed":
                    return False, "Colony failed to become ready"

        except KubernetesClientError as e:
            return False, str(e)


class AddNodeOperation(ColonyOperation):
    def __init__(
        self,
        node_name: str,
        colony_name: str,
        cluster_name: str,
        ip_address: str,
        username: str,
        ssh_key_path: Path,
        namespace: str = "default",
    ):
        super().__init__()
        self.node_name = node_name
        self.colony_name = colony_name
        self.cluster_name = cluster_name
        self.ip_address = ip_address
        self.username = username
        self.ssh_key_path = ssh_key_path
        self.namespace = namespace

    def _create_secret(self) -> Tuple[bool, Optional[str]]:
        ssh_key_name: str = f"{self.colony_name}-{self.node_name}-ssh-key"
        with open(self.ssh_key_path, "r") as key_file:
            ssh_key = key_file.read()

        response = self.resource_manager.core_api.create_namespaced_secret(
            self.namespace,
            body={
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": ssh_key_name,
                },
                "data": {"value": base64.b64encode(ssh_key.encode()).decode()},
            },
        )
        if response.status_code != 201:
            return False, f"Failed to create secret: {response.status_code}"
        return True, ssh_key_name

    def _get_k8s_version_of_colony(self) -> str:
        """Get the Kubernetes version of the colony."""
        colony = self.resource_manager.custom_objects_api.get_namespaced_custom_object(
            group="infra.exalsius.ai",
            version="v1",
            namespace=self.namespace,
            plural="colonies",
            name=self.colony_name,
        )
        k8s_version = colony.get("spec", {}).get("k8sVersion", "v1.27.2+k0s.0")

        # check if k8s version ends with +k0s.0
        # TODO(srnbckr): find a better way to do this
        if not k8s_version.endswith("+k0s.0"):
            k8s_version = k8s_version + "+k0s.0"

        return k8s_version

    def execute(self) -> Tuple[bool, Optional[str]]:
        """Execute the add node operation."""
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        # create a secret with the SSH key
        success, ssh_key_name = self._create_secret()
        if not success:
            return False, ssh_key_name

        k8s_version = self._get_k8s_version_of_colony()

        template = env.get_template("remote-machine.yaml.j2")
        values = {
            "node_name": self.node_name,
            "cluster_name": self.cluster_name,
            "ip_address": self.ip_address,
            "username": self.username,
            "ssh_key_name": ssh_key_name,
            "use_sudo": True,
            "k8s_version": k8s_version,
        }
        rendered = template.render(**values)
        docs = list(yaml.safe_load_all(rendered))
        for doc in docs:
            success, error = self.resource_manager.create_custom_object_from_dict(doc)
            if not success:
                return False, error

        return True, None
