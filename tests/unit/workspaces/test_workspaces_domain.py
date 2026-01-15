import pytest

from exls.workspaces.core.domain import (
    AvailableClusterNodeResources,
    GPUVendorPreference,
    WorkerResources,
    WorkspaceAccessInformation,
    WorkspaceAccessType,
    WorkspaceCluster,
    WorkspaceClusterStatus,
    WorkspaceGPUVendor,
    WorkspaceStatus,
)


@pytest.fixture
def mixed_cluster() -> WorkspaceCluster:
    return WorkspaceCluster(
        id="cluster-1",
        name="mixed-cluster",
        status=WorkspaceClusterStatus.READY,
        available_resources=[
            # AMD Node: 8 GPUs, 96 CPUs, 512GB RAM, 2000GB Storage
            AvailableClusterNodeResources(
                node_id="node-amd-1",
                node_name="node-amd-1",
                node_endpoint="10.0.0.1",
                gpu_type="MI250",
                gpu_vendor=WorkspaceGPUVendor.AMD,
                gpu_count=8,
                cpu_cores=96,
                memory_gb=512,
                storage_gb=2000,
            ),
            # NVIDIA Node: 4 GPUs, 64 CPUs, 256GB RAM, 1000GB Storage
            AvailableClusterNodeResources(
                node_id="node-nvidia-1",
                node_name="node-nvidia-1",
                node_endpoint="10.0.0.2",
                gpu_type="A100",
                gpu_vendor=WorkspaceGPUVendor.NVIDIA,
                gpu_count=4,
                cpu_cores=64,
                memory_gb=256,
                storage_gb=1000,
            ),
            # Small Node: 1 GPU, 4 CPUs, 16GB RAM, 50GB Storage (barely enough)
            AvailableClusterNodeResources(
                node_id="node-small-1",
                node_name="node-small-1",
                node_endpoint="10.0.0.3",
                gpu_type="T4",
                gpu_vendor=WorkspaceGPUVendor.NVIDIA,
                gpu_count=1,
                cpu_cores=4,
                memory_gb=16,
                storage_gb=50,
            ),
        ],
    )


class TestWorkspaceClusterProperties:
    def test_cluster_stats(self, mixed_cluster: WorkspaceCluster):
        assert mixed_cluster.total_nodes == 3
        assert mixed_cluster.total_gpus == 13  # 8 + 4 + 1
        assert mixed_cluster.total_amd_gpus == 8
        assert mixed_cluster.total_nvidia_gpus == 5
        assert mixed_cluster.heterogenous is True

    def test_resource_filtering(self, mixed_cluster: WorkspaceCluster):
        amd_resources = mixed_cluster.available_amd_resources
        assert len(amd_resources) == 1
        assert amd_resources[0].node_id == "node-amd-1"

        nvidia_resources = mixed_cluster.available_nvidia_resources
        assert len(nvidia_resources) == 2


class TestSingleWorkerPartition:
    def test_partition_single_worker_amd(self, mixed_cluster: WorkspaceCluster):
        # Request 1 AMD GPU
        # Node has 8 GPUs, 96 CPUs, 512GB RAM.
        # Per GPU: 12 CPUs, 64GB RAM.
        resource = mixed_cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=1,
            gpu_vendor_preference=GPUVendorPreference.AMD,
            resource_split_tolerance=0.0,
        )

        assert resource is not None
        assert resource.gpu_vendor == WorkspaceGPUVendor.AMD
        assert resource.gpu_count == 1
        assert resource.cpu_cores == 12  # 96 / 8
        assert resource.memory_gb == 64  # 512 / 8
        # Storage: 2000 / 8 = 250. Not full node, so no ephemeral subtraction.
        assert resource.storage_gb == 250

    def test_partition_single_worker_nvidia(self, mixed_cluster: WorkspaceCluster):
        # Request 2 NVIDIA GPUs
        # Best fit node: node-nvidia-1 (4 GPUs, 64 CPUs, 256GB RAM)
        # Per 2 GPUs: 32 CPUs, 128GB RAM.
        resource = mixed_cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=2,
            gpu_vendor_preference=GPUVendorPreference.NVIDIA,
            resource_split_tolerance=0.0,
        )

        assert resource is not None
        assert resource.gpu_vendor == WorkspaceGPUVendor.NVIDIA
        assert resource.gpu_count == 2
        assert resource.cpu_cores == 32  # (64 / 4) * 2
        assert resource.memory_gb == 128  # (256 / 4) * 2
        # Storage: (1000 / 4) * 2 = 500. Not full node, so no ephemeral subtraction.
        assert resource.storage_gb == 500

    def test_partition_single_worker_with_tolerance(
        self, mixed_cluster: WorkspaceCluster
    ):
        # Testing tolerance calculation logic
        # node-amd-1: 96 CPUs. If we request 8 GPUs (full node), we get full resources minus tolerance?
        # The logic: if requested == total, subtract tolerance.

        resource = mixed_cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=8,
            gpu_vendor_preference=GPUVendorPreference.AMD,
            resource_split_tolerance=0.1,
        )

        assert resource is not None
        # Original: 96 CPUs. 10% tolerance = 9. Expected: 87.
        assert resource.cpu_cores == 87
        # Original: 512 RAM. 10% tolerance = 51. Expected: 461.
        assert resource.memory_gb == 461
        # Original: 2000 Storage. 10% tolerance = 200. Expected 1800 - 10 = 1790.
        assert resource.storage_gb == 1790

    def test_partition_single_worker_not_found(self, mixed_cluster: WorkspaceCluster):
        # Request more GPUs than any single node has
        resource = mixed_cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=16,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
        )
        assert resource is None

    def test_partition_single_worker_min_requirements(self):
        # Node with resources below minimum
        # Logic says: cpu < 2, memory < 10, storage < 20 -> continue
        tiny_node = AvailableClusterNodeResources(
            node_id="tiny",
            node_name="tiny",
            node_endpoint="10.0.0.4",
            gpu_type="T4",
            gpu_vendor=WorkspaceGPUVendor.NVIDIA,
            gpu_count=1,
            cpu_cores=1,  # Too small
            memory_gb=8,  # Too small
            storage_gb=10,  # Too small
        )
        cluster = WorkspaceCluster(
            id="c1",
            name="c1",
            status=WorkspaceClusterStatus.READY,
            available_resources=[tiny_node],
        )

        resource = cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=1,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
        )
        assert resource is None

    def test_partition_single_worker_low_memory(self):
        # Node with enough CPU but low memory
        node = AvailableClusterNodeResources(
            node_id="n1",
            node_name="n1",
            node_endpoint="10.0.0.5",
            gpu_type="T4",
            gpu_vendor=WorkspaceGPUVendor.NVIDIA,
            gpu_count=1,
            cpu_cores=10,
            memory_gb=8,
            storage_gb=100,
        )
        cluster = WorkspaceCluster(
            id="c1",
            name="c1",
            status=WorkspaceClusterStatus.READY,
            available_resources=[node],
        )

        resource = cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=1,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
        )
        assert resource is None

    def test_partition_single_worker_low_storage(self):
        # Node with enough CPU/Mem but low storage
        node = AvailableClusterNodeResources(
            node_id="n1",
            node_name="n1",
            node_endpoint="10.0.0.6",
            gpu_type="T4",
            gpu_vendor=WorkspaceGPUVendor.NVIDIA,
            gpu_count=1,
            cpu_cores=10,
            memory_gb=20,
            storage_gb=10,
        )
        cluster = WorkspaceCluster(
            id="c1",
            name="c1",
            status=WorkspaceClusterStatus.READY,
            available_resources=[node],
        )

        resource = cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=1,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
        )
        assert resource is None


class TestWorkerGroupPartition:
    def test_partition_groups_amd_success(self, mixed_cluster: WorkspaceCluster):
        # Request 4 workers, 1 GPU each, AMD
        groups = mixed_cluster.get_resource_partition_for_worker_groups(
            num_workers=4,
            gpu_vendor="amd",
            gpus_per_worker=1,
            resource_split_tolerance=0.0,
        )

        assert len(groups) == 1
        group = groups[0]
        assert group.num_workers == 4
        assert group.worker_resources.gpu_vendor == WorkspaceGPUVendor.AMD
        assert group.worker_resources.gpu_count == 1
        # Should correspond to node-amd-1 split (8 gpus total)
        # 96 / 8 = 12 CPUs
        assert group.worker_resources.cpu_cores == 12

    def test_partition_groups_nvidia_success(self, mixed_cluster: WorkspaceCluster):
        # Request 4 workers, 1 GPU each, NVIDIA
        # We have 5 NVIDIA GPUs total (4 on node 1, 1 on node 2).
        # Logic takes MINIMUM split across all NVIDIA nodes.
        # node-nvidia-1: 64/4 = 16 CPUs/GPU
        # node-small-1: 4/1 = 4 CPUs/GPU
        # Min is 4 CPUs.

        groups = mixed_cluster.get_resource_partition_for_worker_groups(
            num_workers=4,
            gpu_vendor="nvidia",
            gpus_per_worker=1,
            resource_split_tolerance=0.0,
        )

        assert len(groups) == 1
        group = groups[0]
        assert group.num_workers == 4
        # Should define resources based on the weakest node (min split)
        assert group.worker_resources.cpu_cores == 4
        assert group.worker_resources.memory_gb == 16  # min(256/4=64, 16/1=16) -> 16

    def test_partition_groups_auto_heterogenous(self, mixed_cluster: WorkspaceCluster):
        # Total GPUs: 13 (8 AMD, 5 NVIDIA)
        # Request 13 workers, 1 GPU each, AUTO.
        # AMD ratio: 8/13 ~ 0.615 -> 13 * 0.615 = 8 workers
        # NVIDIA ratio: 5/13 ~ 0.384 -> 5 workers

        groups = mixed_cluster.get_resource_partition_for_worker_groups(
            num_workers=13,
            gpu_vendor="auto",
            gpus_per_worker=1,
            resource_split_tolerance=0.0,
        )

        assert len(groups) == 2
        # Order depends on implementation but likely AMD then NVIDIA or vice versa
        amd_group = next(
            g for g in groups if g.worker_resources.gpu_vendor == WorkspaceGPUVendor.AMD
        )
        nvidia_group = next(
            g
            for g in groups
            if g.worker_resources.gpu_vendor == WorkspaceGPUVendor.NVIDIA
        )

        assert amd_group.num_workers == 8
        assert nvidia_group.num_workers == 5

    def test_partition_groups_auto_adjustment_nvidia_limit(self):
        # 3 AMD, 3 NVIDIA. Request 3 workers @ 2 GPUs/worker. Total 6 GPUs needed.
        # AMD Ratio: 0.5. Initial Split: 1 AMD (2 GPUs), 2 NVIDIA (4 GPUs).
        # NVIDIA (4 GPUs) > Available (3).
        # Fallback Logic:
        # NVIDIA workers = 3 // 2 = 1.
        # AMD workers = 3 - 1 = 2.
        # AMD needs 4 GPUs. Available 3.
        # This will fail inside `_get_resource_partition_for_worker_group`? No, that function assumes validation done?
        # Actually `_get_resource_partition_for_worker_group` splits resources.

        c = WorkspaceCluster(
            id="c2",
            name="c2",
            status=WorkspaceClusterStatus.READY,
            available_resources=[
                AvailableClusterNodeResources(
                    node_id="n1",
                    node_name="n1",
                    node_endpoint="10.0.0.7",
                    gpu_type="X",
                    gpu_vendor=WorkspaceGPUVendor.AMD,
                    gpu_count=3,
                    cpu_cores=30,
                    memory_gb=30,
                    storage_gb=30,
                ),
                AvailableClusterNodeResources(
                    node_id="n2",
                    node_name="n2",
                    node_endpoint="10.0.0.8",
                    gpu_type="Y",
                    gpu_vendor=WorkspaceGPUVendor.NVIDIA,
                    gpu_count=3,
                    cpu_cores=30,
                    memory_gb=30,
                    storage_gb=30,
                ),
            ],
        )

        groups = c.get_resource_partition_for_worker_groups(
            num_workers=3,
            gpu_vendor="auto",
            gpus_per_worker=2,
            resource_split_tolerance=0.0,
        )

        # Expect NVIDIA limit trigger.
        # Result: NVIDIA=1, AMD=2.
        amd_group = next(
            g for g in groups if g.worker_resources.gpu_vendor == WorkspaceGPUVendor.AMD
        )
        nvidia_group = next(
            g
            for g in groups
            if g.worker_resources.gpu_vendor == WorkspaceGPUVendor.NVIDIA
        )

        assert nvidia_group.num_workers == 1
        assert amd_group.num_workers == 2

    def test_insufficient_resources_specific_vendor(
        self, mixed_cluster: WorkspaceCluster
    ):
        with pytest.raises(ValueError, match="does not have enough AMD GPUs"):
            mixed_cluster.get_resource_partition_for_worker_groups(
                num_workers=10,  # only 8 available
                gpu_vendor="amd",
                gpus_per_worker=1,
            )
        with pytest.raises(ValueError, match="does not have enough NVIDIA GPUs"):
            mixed_cluster.get_resource_partition_for_worker_groups(
                num_workers=6,  # only 5 available
                gpu_vendor="nvidia",
                gpus_per_worker=1,
            )

    def test_insufficient_resources_total(self, mixed_cluster: WorkspaceCluster):
        with pytest.raises(ValueError, match="does not have enough GPUs available"):
            mixed_cluster.get_resource_partition_for_worker_groups(
                num_workers=20,  # only 13 available total
                gpu_vendor="auto",
                gpus_per_worker=1,
            )

    def test_partition_groups_with_tolerance(self, mixed_cluster: WorkspaceCluster):
        # Test tolerance application in worker groups
        # AMD Node: 96 CPUs / 8 GPUs = 12 CPUs per GPU.
        # With 10% tolerance: 12 * 0.9 = 10.8 -> 10 CPUs.

        groups = mixed_cluster.get_resource_partition_for_worker_groups(
            num_workers=4,
            gpu_vendor="amd",
            gpus_per_worker=1,
            resource_split_tolerance=0.1,
        )

        group = groups[0]
        # 12 * 0.9 = 10.
        assert group.worker_resources.cpu_cores == 10

        # Memory: 512 / 8 = 64. 64 * 0.9 = 57.6 -> 57.
        assert group.worker_resources.memory_gb == 57


class TestWorkspaceValueObjects:
    def test_formatted_access_info_ssh(self):
        # Case 1: SSH standard port
        wai = WorkspaceAccessInformation(
            access_type=WorkspaceAccessType.NODE_PORT,
            access_protocol="ssh",
            external_ips=["1.2.3.4"],
            port_number=22,
        )
        assert wai.formatted_access_information == "ssh dev@1.2.3.4"

        # Case 2: SSH non-standard port
        wai = WorkspaceAccessInformation(
            access_type=WorkspaceAccessType.NODE_PORT,
            access_protocol="ssh",
            external_ips=["1.2.3.4"],
            port_number=2222,
        )
        assert wai.formatted_access_information == "ssh -p 2222 dev@1.2.3.4"

    def test_formatted_access_info_http(self):
        wai = WorkspaceAccessInformation(
            access_type=WorkspaceAccessType.INGRESS,
            access_protocol="http",
            external_ips=["1.2.3.4"],
            port_number=80,
        )
        assert wai.formatted_access_information == "http://1.2.3.4:80"

    def test_formatted_access_info_pending(self):
        wai = WorkspaceAccessInformation(
            access_type=WorkspaceAccessType.INGRESS,
            access_protocol="http",
            external_ips=[],
            port_number=80,
        )
        assert wai.formatted_access_information == "<pending>"

    def test_enums_from_str(self):
        assert WorkspaceClusterStatus.from_str("READY") == WorkspaceClusterStatus.READY
        assert (
            WorkspaceClusterStatus.from_str("INVALID") == WorkspaceClusterStatus.UNKNOWN
        )

        assert WorkspaceStatus.from_str("RUNNING") == WorkspaceStatus.RUNNING
        assert WorkspaceStatus.from_str("invalid") == WorkspaceStatus.UNKNOWN

        assert WorkspaceGPUVendor.from_str("nvidia") == WorkspaceGPUVendor.NVIDIA
        assert WorkspaceGPUVendor.from_str("invalid") == WorkspaceGPUVendor.UNKNOWN

        assert (
            WorkspaceAccessType.from_str("node_port") == WorkspaceAccessType.NODE_PORT
        )
        assert WorkspaceAccessType.from_str("invalid") == WorkspaceAccessType.UNKNOWN


class TestClusterResourceChecks:
    def test_has_enough_resources(self, mixed_cluster: WorkspaceCluster):
        # Request valid resources
        req = WorkerResources(
            gpu_count=1,
            cpu_cores=10,
            memory_gb=10,
            storage_gb=10,
        )
        assert mixed_cluster.has_enough_resources(req) is True

        # Request too many GPUs
        req_too_many_gpu = WorkerResources(
            gpu_count=100,
            cpu_cores=10,
            memory_gb=10,
            storage_gb=10,
            gpu_vendor=WorkspaceGPUVendor.AMD,  # Added vendor to avoid type error if strict
        )
        assert mixed_cluster.has_enough_resources(req_too_many_gpu) is False

        # Request too much CPU
        req_too_many_cpu = WorkerResources(
            gpu_count=1,
            cpu_cores=1000,
            memory_gb=10,
            storage_gb=10,
        )
        assert mixed_cluster.has_enough_resources(req_too_many_cpu) is False

        # Request too much Memory
        req_too_many_mem = WorkerResources(
            gpu_count=1,
            cpu_cores=10,
            memory_gb=10000,
            storage_gb=10,
        )
        assert mixed_cluster.has_enough_resources(req_too_many_mem) is False

        # Request too much Storage
        req_too_many_storage = WorkerResources(
            gpu_count=1,
            cpu_cores=10,
            memory_gb=10,
            storage_gb=10000,
        )
        assert mixed_cluster.has_enough_resources(req_too_many_storage) is False

    def test_partition_single_worker_storage_constraints(self):
        # Create a node with barely enough storage
        node = AvailableClusterNodeResources(
            node_id="n1",
            node_name="n1",
            node_endpoint="10.0.0.9",
            gpu_type="T4",
            gpu_vendor=WorkspaceGPUVendor.NVIDIA,
            gpu_count=1,
            cpu_cores=10,
            memory_gb=20,
            storage_gb=20,  # Exactly 20GB
        )
        cluster = WorkspaceCluster(
            id="c1",
            name="c1",
            status=WorkspaceClusterStatus.READY,
            available_resources=[node],
        )

        # Request 1 GPU (full node).
        # requested_storage = 20.
        # Minus tolerance (0.1) -> 20 - 2 = 18.
        # Minus 10GB ephemeral -> 8.
        # 8 < 10 -> Should fail (continue loop -> return None).

        resource = cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=1,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
            resource_split_tolerance=0.1,
        )
        assert resource is None


class TestPartitionEdgeCases:
    def test_partition_single_worker_partial_node_no_tolerance(
        self, mixed_cluster: WorkspaceCluster
    ):
        """
        Verifies that tolerance is NOT applied when the request does not consume
        the full node, preventing unexpected resource reduction on partial nodes.
        """
        # Node 'node-amd-1': 8 GPUs, 96 CPUs.
        # Request 4 GPUs (50%).
        # Expected: 50% of CPUs = 48. Tolerance (10%) should NOT be applied.
        resource = mixed_cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=4,
            gpu_vendor_preference=GPUVendorPreference.AMD,
            resource_split_tolerance=0.1,
        )
        assert resource is not None
        assert resource.gpu_count == 4
        assert resource.cpu_cores == 48  # Exact half, no tolerance subtraction

    def test_partition_single_worker_cpu_only(self, mixed_cluster: WorkspaceCluster):
        """
        Verifies behavior when requesting 0 GPUs (CPU-only workspace) on a GPU node.
        """
        # Should return minimal resources (1 CPU, 1 GB) on a GPU node according to current logic.
        resource = mixed_cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=0,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
            resource_split_tolerance=0.0,
        )

        assert resource is not None
        assert resource.gpu_count == 0
        assert (
            resource.gpu_vendor != WorkspaceGPUVendor.NO_GPU
        )  # Inherits vendor (AMD in this case likely as it's first)
        assert resource.cpu_cores == 1
        assert resource.memory_gb == 1

    def test_partition_single_worker_cpu_only_on_cpu_node(self):
        # Node with NO GPUs
        cpu_node = AvailableClusterNodeResources(
            node_id="cpu1",
            node_name="cpu1",
            node_endpoint="10.0.0.10",
            gpu_vendor=WorkspaceGPUVendor.NO_GPU,
            gpu_count=0,
            cpu_cores=32,
            memory_gb=64,
            storage_gb=100,
            gpu_type="None",
        )
        cluster = WorkspaceCluster(
            id="c_cpu",
            name="c_cpu",
            status=WorkspaceClusterStatus.READY,
            available_resources=[cpu_node],
        )

        resource = cluster.get_resource_partition_for_single_worker(
            num_requested_gpus=0,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
            resource_split_tolerance=0.1,
        )

        assert resource is not None
        assert resource.gpu_count == 0
        # Should get full node resources (minus tolerance)
        # 32 * 0.1 = 3.2 -> 3 tolerance. 32 - 3 = 29.
        assert resource.cpu_cores == 29
        # 64 * 0.1 = 6.4 -> 6 tolerance. 64 - 6 = 58.
        assert resource.memory_gb == 58

    def test_partition_groups_heterogenous_constraints(self):
        """
        Verifies that a worker group is constrained by the weakest node
        in the set (homogenous worker sizing).
        """
        # 1 Super Node, 1 Weak Node
        super_node = AvailableClusterNodeResources(
            node_id="super",
            node_name="super",
            node_endpoint="10.0.0.12",
            gpu_vendor=WorkspaceGPUVendor.NVIDIA,
            gpu_count=1,
            cpu_cores=100,
            memory_gb=100,
            storage_gb=100,
            gpu_type="A100",
        )
        weak_node = AvailableClusterNodeResources(
            node_id="weak",
            node_name="weak",
            node_endpoint="10.0.0.11",
            gpu_vendor=WorkspaceGPUVendor.NVIDIA,
            gpu_count=1,
            cpu_cores=10,
            memory_gb=10,
            storage_gb=10,
            gpu_type="A100",
        )
        cluster = WorkspaceCluster(
            id="c",
            name="c",
            status=WorkspaceClusterStatus.READY,
            available_resources=[super_node, weak_node],
        )

        groups = cluster.get_resource_partition_for_worker_groups(
            num_workers=2,
            gpu_vendor="nvidia",
            gpus_per_worker=1,
            resource_split_tolerance=0.0,
        )

        assert len(groups) == 1
        # The worker definition should be capped by the weak node (10 CPUs), not the super node.
        assert groups[0].worker_resources.cpu_cores == 10
        assert groups[0].worker_resources.memory_gb == 10
