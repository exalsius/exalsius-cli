from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import questionary
import yaml
from exalsius_api_client.models.base_node import BaseNode

from exalsius.clusters.display import ClusterInteractiveDisplay
from exalsius.clusters.models import ClusterConfigNodeDTO, ClusterType, GPUType
from exalsius.clusters.service import ClustersService
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.nodes.service import NodeService
from exalsius.utils import commons as utils


class ClusterInteractiveConfig:
    """Internal state for interactive cluster creation."""

    def __init__(self):
        self.name: str = ""
        self.cluster_type: ClusterType = ClusterType.REMOTE
        self.gpu_type: GPUType = GPUType.NVIDIA
        self.diloco_enabled: bool = False
        self.telemetry_enabled: bool = False
        self.node_ids: List[str] = []
        self.node_roles: Dict[str, str] = {}  # node_id -> role
        self.should_deploy: bool = False


class ClusterInteractiveFlow:
    """Interactive flow for cluster creation."""

    def __init__(
        self,
        service: ClustersService,
        node_service: NodeService,
        display_manager: ClusterInteractiveDisplay,
    ):
        self.service = service
        self.node_service = node_service
        self.display_manager = display_manager
        self.config = ClusterInteractiveConfig()
        self.available_nodes: List[BaseNode] = []

    def run(self) -> Optional[str]:
        """Main orchestration method, returns cluster_id or None."""
        self.display_manager.display_welcome(
            "🚀 Cluster Creation - Interactive Mode",
            "This will guide you through creating a new cluster.\n",
        )

        # Step 1: Cluster Configuration
        self.display_manager.display_section("📋 Step 1: Cluster Configuration")
        self._prompt_cluster_config()

        # Step 2: Node Selection
        self.display_manager.display_section("🖥️  Step 2: Node Selection")
        self._prompt_node_selection()

        if self.config.node_ids:
            # Step 3: Node Roles
            self.display_manager.display_section("👔 Step 3: Node Roles")
            self._prompt_node_roles()

        # Step 4: Summary & Confirmation
        self.display_manager.display_section("📊 Summary")
        if not self._display_summary():
            return None

        # Create cluster
        cluster_id = self._create_cluster()

        if cluster_id:
            # Step 5: Deployment
            self.display_manager.display_section("🚀 Deployment")
            self._prompt_deployment(cluster_id)

            # Step 6: Save configuration to file
            self._save_config_to_file(cluster_id)

        return cluster_id

    def _prompt_cluster_config(self) -> None:
        """Collect cluster configuration via prompts."""
        self.config.name = questionary.text(
            "Cluster name:", default=utils.generate_random_name(prefix="exls-cluster")
        ).ask()

        self.config.cluster_type = ClusterType(
            questionary.select(
                "Cluster type:",
                choices=[
                    questionary.Choice(
                        "Remote (self-managed nodes)", ClusterType.REMOTE
                    ),
                    questionary.Choice("Cloud (cloud instances)", ClusterType.CLOUD),
                    questionary.Choice(
                        "Adopted (existing k8s cluster)", ClusterType.ADOPTED
                    ),
                ],
                default=ClusterType.REMOTE,
            ).ask()
        )

        self.config.gpu_type = GPUType(
            questionary.select(
                "GPU type:",
                choices=[
                    questionary.Choice("NVIDIA (default)", GPUType.NVIDIA),
                    questionary.Choice("AMD", GPUType.AMD),
                    questionary.Choice("None (no GPU support)", GPUType.NONE),
                ],
                default=GPUType.NVIDIA,
            ).ask()
        )

        self.config.diloco_enabled = questionary.confirm(
            "Enable Diloco/Volcano workload support?", default=False
        ).ask()

        self.config.telemetry_enabled = questionary.confirm(
            "Enable telemetry?", default=False
        ).ask()

    def _prompt_node_selection(self) -> None:
        """Show available nodes and collect selections."""
        try:
            self.available_nodes = self.node_service.list_nodes(None, None)
        except ServiceError as e:
            self.display_manager.display_error(
                ErrorDTO(
                    message=e.message,
                    error_type=e.error_type,
                    error_code=e.error_code,
                )
            )
            self.available_nodes = []

        if not self.available_nodes:
            self.display_manager.display_info(
                "No nodes available. You can add nodes later with 'exls clusters add-nodes'."
            )
            return

        # Show nodes table
        self.display_manager.display_available_nodes(self.available_nodes)

        # Build choices for checkbox
        choices = [
            questionary.Choice(
                title=f"{node.hostname} ({node.id[:12]}) - {node.node_status}",
                value=node.id,
            )
            for node in self.available_nodes
        ]

        selected = questionary.checkbox(
            "Select nodes to add (Space to select, Enter to confirm):", choices=choices
        ).ask()

        self.config.node_ids = selected if selected else []

    def _prompt_node_roles(self) -> None:
        """Assign roles to selected nodes."""
        for node_id in self.config.node_ids:
            node_display = next(
                (n.hostname for n in self.available_nodes if n.id == node_id),
                node_id[:12],
            )

            role = questionary.select(
                f"Role for {node_display}:",
                choices=[
                    questionary.Choice("Worker (default)", "WORKER"),
                    questionary.Choice("Control Plane", "CONTROL_PLANE"),
                ],
                default="WORKER",
            ).ask()

            self.config.node_roles[node_id] = role

    def _display_summary(self) -> bool:
        """Show summary and confirm creation."""
        self.display_manager.display_cluster_creation_summary(self.config)

        return questionary.confirm(
            "Create cluster with these settings?", default=True
        ).ask()

    def _create_cluster(self) -> str:
        """Create cluster via service."""
        # Extract node IDs by role
        control_plane_ids = [
            node_id
            for node_id, role in self.config.node_roles.items()
            if role == "CONTROL_PLANE"
        ]
        worker_ids = [
            node_id
            for node_id, role in self.config.node_roles.items()
            if role == "WORKER"
        ]

        cluster_id = self.service.create_cluster(
            name=self.config.name,
            cluster_type=self.config.cluster_type,
            gpu_type=self.config.gpu_type,
            diloco=self.config.diloco_enabled,
            telemetry_enabled=self.config.telemetry_enabled,
            control_plane_node_ids=control_plane_ids if control_plane_ids else None,
            worker_node_ids=worker_ids if worker_ids else None,
        )

        self.display_manager.display_success(
            f"Cluster {cluster_id} created successfully."
        )
        return cluster_id

    def _prompt_deployment(self, cluster_id: str) -> None:
        """Prompt for deployment and execute if requested."""
        should_deploy = questionary.confirm(
            "Would you like to deploy the cluster now?", default=True
        ).ask()

        if should_deploy:
            try:
                self.service.deploy_cluster(cluster_id)
                self.display_manager.display_success(
                    f"Cluster {cluster_id} deployed successfully!"
                )
            except ServiceError as e:
                self.display_manager.display_error(
                    ErrorDTO(
                        message=e.message,
                        error_type=e.error_type,
                        error_code=e.error_code,
                    )
                )

    def _save_config_to_file(self, cluster_id: str) -> None:
        """Save the cluster configuration to a YAML file in the current directory."""

        config_data: Dict[str, Any] = {
            "name": self.config.name,
            "cluster_type": self.config.cluster_type.value,
            "gpu_type": self.config.gpu_type.value,
            "diloco_enabled": self.config.diloco_enabled,
            "telemetry_enabled": self.config.telemetry_enabled,
            "deploy": False,  # Already deployed if user chose to
        }

        if self.config.node_ids:
            config_data["nodes"] = [
                ClusterConfigNodeDTO(
                    node_id=node_id, role=self.config.node_roles.get(node_id, "WORKER")
                ).model_dump()
                for node_id in self.config.node_ids
            ]

        safe_name = "".join(
            c if c.isalnum() or c in "-_" else "-" for c in self.config.name
        )
        filename = f"{safe_name}-cluster.yaml"
        filepath = Path.cwd() / filename

        if filepath.exists():
            counter = 1
            while filepath.exists():
                filename = f"{safe_name}-cluster-{counter}.yaml"
                filepath = Path.cwd() / filename
                counter += 1

        try:
            with open(filepath, "w") as f:
                f.write("# Cluster configuration generated by exalsius CLI\n")
                f.write(f"# Cluster ID: {cluster_id}\n")
                f.write(
                    f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"# Usage: exls clusters create --config {filepath.name}\n\n")

                yaml.dump(
                    config_data, f, default_flow_style=False, sort_keys=False, indent=2
                )

            self.display_manager.display_success(
                f"Configuration saved to: {filepath.name}"
            )
            self.display_manager.display_info(
                f"You can reuse this config with: exls clusters create --config {filepath.name}"
            )
        except Exception as e:
            # Don't fail the entire operation if file save fails
            self.display_manager.display_error(
                ErrorDTO(message=f"Warning: Could not save config file: {e}")
            )
