from datetime import datetime

from exls.clusters.core.domain import (
    Cluster,
    ClusterNode,
    ClusterNodeResources,
    ClusterNodeRole,
    ClusterNodeStatus,
    ClusterStatus,
    ClusterType,
)


def test_cluster_node_resources_creation() -> None:
    resources = ClusterNodeResources(
        gpu_type="nvidia-tesla-t4",
        gpu_vendor="NVIDIA",
        gpu_count=1,
        cpu_cores=4,
        memory_gb=16,
        storage_gb=100,
    )
    assert resources.gpu_type == "nvidia-tesla-t4"
    assert resources.gpu_vendor == "NVIDIA"
    assert resources.gpu_count == 1
    assert resources.cpu_cores == 4
    assert resources.memory_gb == 16
    assert resources.storage_gb == 100


def test_cluster_node_status_from_str() -> None:
    assert ClusterNodeStatus.from_str("AVAILABLE") == ClusterNodeStatus.AVAILABLE
    assert ClusterNodeStatus.from_str("available") == ClusterNodeStatus.AVAILABLE
    assert ClusterNodeStatus.from_str("unknown_status") == ClusterNodeStatus.UNKNOWN


def test_cluster_node_role_from_str() -> None:
    assert ClusterNodeRole.from_str("WORKER") == ClusterNodeRole.WORKER
    assert ClusterNodeRole.from_str("worker") == ClusterNodeRole.WORKER
    assert ClusterNodeRole.from_str("invalid") == ClusterNodeRole.UNKNOWN


def test_cluster_node_creation() -> None:
    resources = ClusterNodeResources(
        gpu_type="none",
        gpu_vendor="none",
        gpu_count=0,
        cpu_cores=2,
        memory_gb=4,
        storage_gb=50,
    )
    node = ClusterNode(
        id="node-123",
        role=ClusterNodeRole.WORKER,
        hostname="worker-1",
        username="user",
        ssh_key_id="key-1",
        status=ClusterNodeStatus.AVAILABLE,
        endpoint="192.168.1.100",
        free_resources=resources,
        occupied_resources=resources,
    )
    assert node.id == "node-123"
    assert node.role == ClusterNodeRole.WORKER
    assert node.hostname == "worker-1"
    assert node.free_resources.cpu_cores == 2


def test_cluster_type_from_str() -> None:
    assert ClusterType.from_str("REMOTE") == ClusterType.REMOTE
    assert ClusterType.from_str("remote") == ClusterType.REMOTE
    assert ClusterType.from_str("invalid") == ClusterType.UNKNOWN


def test_cluster_status_from_str() -> None:
    # ClusterStatus.from_str does NOT currently normalize to uppercase
    assert ClusterStatus.from_str("READY") == ClusterStatus.READY
    assert ClusterStatus.from_str("PENDING") == ClusterStatus.PENDING
    assert ClusterStatus.from_str("invalid") == ClusterStatus.UNKNOWN


def test_cluster_creation() -> None:
    resources = ClusterNodeResources(
        gpu_type="none",
        gpu_vendor="none",
        gpu_count=0,
        cpu_cores=2,
        memory_gb=4,
        storage_gb=50,
    )
    node = ClusterNode(
        id="node-1",
        role=ClusterNodeRole.WORKER,
        hostname="h1",
        username="u",
        ssh_key_id="k",
        status=ClusterNodeStatus.AVAILABLE,
        endpoint="e",
        free_resources=resources,
        occupied_resources=resources,
    )

    now = datetime.now()
    cluster = Cluster(
        id="c-1",
        name="test-cluster",
        status=ClusterStatus.READY,
        type=ClusterType.CLOUD,
        created_at=now,
        updated_at=None,
        nodes=[node],
    )

    assert cluster.id == "c-1"
    assert cluster.name == "test-cluster"
    assert cluster.status == ClusterStatus.READY
    assert cluster.type == ClusterType.CLOUD
    assert cluster.created_at == now
    assert cluster.updated_at is None
    assert len(cluster.nodes) == 1
    assert cluster.nodes[0].id == "node-1"
