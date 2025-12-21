from datetime import datetime

import pytest
from pydantic import ValidationError

from exls.nodes.core.domain import (
    CloudNode,
    NodeResources,
    NodeStatus,
    SelfManagedNode,
)


class TestNodeStatus:
    def test_node_status_enum_values(self):
        """Test that enum values are correct."""
        assert NodeStatus.DISCOVERING == "DISCOVERING"
        assert NodeStatus.AVAILABLE == "AVAILABLE"
        assert NodeStatus.ADDED == "ADDED"
        assert NodeStatus.DEPLOYED == "DEPLOYED"
        assert NodeStatus.FAILED == "FAILED"
        assert NodeStatus.UNKNOWN == "UNKNOWN"

    def test_from_str_valid(self):
        """Test parsing valid status strings."""
        assert NodeStatus.from_str("DISCOVERING") == NodeStatus.DISCOVERING
        assert NodeStatus.from_str("discovering") == NodeStatus.DISCOVERING
        assert NodeStatus.from_str("AVAILABLE") == NodeStatus.AVAILABLE
        assert NodeStatus.from_str("Available") == NodeStatus.AVAILABLE

    def test_from_str_invalid(self):
        """Test parsing invalid status strings returns UNKNOWN."""
        assert NodeStatus.from_str("INVALID_STATUS") == NodeStatus.UNKNOWN
        assert NodeStatus.from_str("") == NodeStatus.UNKNOWN
        assert NodeStatus.from_str("random") == NodeStatus.UNKNOWN


class TestNodeResources:
    def test_create_valid_resources(self):
        """Test creating NodeResources with valid data."""
        resources = NodeResources(
            gpu_type="nvidia-a100",
            gpu_vendor="nvidia",
            gpu_count=4,
            cpu_cores=64,
            memory_gb=256,
            storage_gb=1000,
        )
        assert resources.gpu_type == "nvidia-a100"
        assert resources.gpu_vendor == "nvidia"
        assert resources.gpu_count == 4
        assert resources.cpu_cores == 64
        assert resources.memory_gb == 256
        assert resources.storage_gb == 1000

    def test_validation_strict_types(self):
        """Test that strict types are enforced (no coercion for strict types)."""
        # Pydantic StrictInt/StrictStr will raise error if type doesn't match
        with pytest.raises(ValidationError):
            NodeResources(
                gpu_type=123,  # type: ignore # Should be string
                gpu_vendor="nvidia",
                gpu_count=4,
                cpu_cores=64,
                memory_gb=256,
                storage_gb=1000,
            )

        with pytest.raises(ValidationError):
            NodeResources(
                gpu_type="nvidia-a100",
                gpu_vendor="nvidia",
                gpu_count="4",  # type: ignore # Should be int
                cpu_cores=64,
                memory_gb=256,
                storage_gb=1000,
            )


class TestCloudNode:
    def test_create_valid_cloud_node(self):
        """Test creating a CloudNode with valid data."""
        resources = NodeResources(
            gpu_type="nvidia-a100",
            gpu_vendor="nvidia",
            gpu_count=4,
            cpu_cores=64,
            memory_gb=256,
            storage_gb=1000,
        )
        now = datetime.now()

        node = CloudNode(
            id="node-123",
            hostname="cloud-worker-1",
            import_time=now,
            status=NodeStatus.AVAILABLE,
            resources=resources,
            provider="aws",
            instance_type="p4d.24xlarge",
            price_per_hour="32.77",
        )

        assert node.id == "node-123"
        assert node.hostname == "cloud-worker-1"
        assert node.import_time == now
        assert node.status == NodeStatus.AVAILABLE
        assert node.resources == resources
        assert node.provider == "aws"
        assert node.instance_type == "p4d.24xlarge"
        assert node.price_per_hour == "32.77"

    def test_missing_required_fields(self):
        """Test that validation fails when required fields are missing."""
        with pytest.raises(ValidationError):
            CloudNode(  # type: ignore
                id="node-123",
                # hostname missing
                import_time=datetime.now(),
                status=NodeStatus.AVAILABLE,
                resources=NodeResources(
                    gpu_type="t4",
                    gpu_vendor="nvidia",
                    gpu_count=1,
                    cpu_cores=4,
                    memory_gb=16,
                    storage_gb=100,
                ),
                provider="gcp",
                instance_type="n1-standard-4",
                price_per_hour="1.5",
            )

    def test_optional_import_time(self):
        """Test that import_time can be None if allowed (it is marked Optional in domain)."""
        # Looking at domain.py: import_time: Optional[datetime] = Field(...)
        # However, Field(...) means it is required, even if type is Optional.
        # Let's verify if None is accepted as a value.

        resources = NodeResources(
            gpu_type="t4",
            gpu_vendor="nvidia",
            gpu_count=1,
            cpu_cores=4,
            memory_gb=16,
            storage_gb=100,
        )

        node = CloudNode(
            id="node-123",
            hostname="cloud-worker-1",
            import_time=None,
            status=NodeStatus.AVAILABLE,
            resources=resources,
            provider="aws",
            instance_type="p4d.24xlarge",
            price_per_hour="32.77",
        )
        assert node.import_time is None


class TestSelfManagedNode:
    def test_create_valid_self_managed_node(self):
        """Test creating a SelfManagedNode with valid data."""
        resources = NodeResources(
            gpu_type="rtx-3090",
            gpu_vendor="nvidia",
            gpu_count=1,
            cpu_cores=16,
            memory_gb=64,
            storage_gb=500,
        )
        now = datetime.now()

        node = SelfManagedNode(
            id="local-node-1",
            hostname="onprem-server",
            import_time=now,
            status=NodeStatus.ADDED,
            resources=resources,
            ssh_key_id="key-xyz",
            ssh_key_name="my-key",
            username="ubuntu",
            endpoint="192.168.1.100",
        )

        assert node.id == "local-node-1"
        assert node.hostname == "onprem-server"
        assert isinstance(node, SelfManagedNode)
        assert node.ssh_key_id == "key-xyz"
        assert node.ssh_key_name == "my-key"
        assert node.username == "ubuntu"
        assert node.endpoint == "192.168.1.100"

    def test_default_values(self):
        """Test default values for optional fields."""
        resources = NodeResources(
            gpu_type="rtx-3090",
            gpu_vendor="nvidia",
            gpu_count=1,
            cpu_cores=16,
            memory_gb=64,
            storage_gb=500,
        )

        node = SelfManagedNode(
            id="local-node-1",
            hostname="onprem-server",
            import_time=None,
            status=NodeStatus.ADDED,
            resources=resources,
            ssh_key_id="key-xyz",
            username="ubuntu",
            # ssh_key_name and endpoint omitted
        )

        assert node.ssh_key_name == ""  # Default from domain.py
        assert node.endpoint is None  # Default from domain.py
