import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from exls.clusters.core.domain import (
    Cluster,
    ClusterNode,
    ClusterNodeResources,
    ClusterNodeRole,
    ClusterNodeStatus,
    ClusterStatus,
    ClusterType,
)
from exls.clusters.core.ports.operations import ClusterOperations
from exls.clusters.core.ports.provider import (
    ClusterNodeImportIssue,
    ClusterNodesImportResult,
    NodesProvider,
)
from exls.clusters.core.ports.repository import (
    ClusterRepository,
)
from exls.clusters.core.requests import (
    ClusterDeployRequest,
    ClusterNodeSpecification,
)
from exls.clusters.core.results import ClusterScaleResult, DeployClusterResult
from exls.clusters.core.service import ClustersService
from exls.shared.core.exceptions import ServiceError
from exls.shared.core.ports.file import FileWritePort


class TestClustersService(unittest.TestCase):
    def setUp(self):
        self.mock_ops = MagicMock(spec=ClusterOperations)
        self.mock_repo = MagicMock(spec=ClusterRepository)
        self.mock_provider = MagicMock(spec=NodesProvider)
        self.mock_file_writer = MagicMock(spec=FileWritePort)

        self.service = ClustersService(
            clusters_operations=self.mock_ops,
            clusters_repository=self.mock_repo,
            nodes_provider=self.mock_provider,
            file_write_adapter=self.mock_file_writer,
        )

        # Common test data
        self.resources = ClusterNodeResources(
            gpu_type="NVIDIA A100",
            gpu_vendor="NVIDIA",
            gpu_count=1,
            cpu_cores=8,
            memory_gb=32,
            storage_gb=100,
        )

        self.node1 = ClusterNode(
            id="node-1",
            role=ClusterNodeRole.WORKER,
            hostname="host1",
            username="user",
            ssh_key_id="key1",
            status=ClusterNodeStatus.AVAILABLE,
            endpoint="1.2.3.4",
            free_resources=self.resources,
            occupied_resources=self.resources,
        )

        self.cluster1 = Cluster(
            id="cluster-1",
            name="test-cluster",
            status=ClusterStatus.READY,
            type=ClusterType.REMOTE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            nodes=[self.node1],
        )

    def test_list_clusters(self):
        self.mock_repo.list.return_value = [self.cluster1]

        result = self.service.list_clusters()

        self.assertEqual(result, [self.cluster1])
        self.mock_repo.list.assert_called_once_with(status=None)

    def test_get_cluster(self):
        self.mock_repo.get.return_value = self.cluster1

        result = self.service.get_cluster("cluster-1")

        self.assertEqual(result, self.cluster1)
        self.mock_repo.get.assert_called_once_with(cluster_id="cluster-1")

    def test_delete_cluster(self):
        self.service.delete_cluster("cluster-1")
        self.mock_repo.delete.assert_called_once_with(cluster_id="cluster-1")

    def test_get_dashboard_url(self):
        self.mock_repo.get.return_value = self.cluster1
        self.mock_ops.get_dashboard_url.return_value = "http://dashboard"

        url = self.service.get_dashboard_url("cluster-1")

        self.assertEqual(url, "http://dashboard")
        self.mock_ops.get_dashboard_url.assert_called_once_with(cluster_id="cluster-1")

    def test_get_dashboard_url_invalid_status(self):
        deploying_cluster = self.cluster1.model_copy(
            update={"status": ClusterStatus.DEPLOYING}
        )
        self.mock_repo.get.return_value = deploying_cluster

        with self.assertRaises(ServiceError) as cm:
            self.service.get_dashboard_url("cluster-1")
        self.assertIn("still deploying", str(cm.exception))

        failed_cluster = self.cluster1.model_copy(
            update={"status": ClusterStatus.FAILED}
        )
        self.mock_repo.get.return_value = failed_cluster

        with self.assertRaises(ServiceError) as cm:
            self.service.get_dashboard_url("cluster-1")
        self.assertIn("deployment failed", str(cm.exception))

    def test_import_kubeconfig(self):
        self.mock_repo.get.return_value = self.cluster1
        self.mock_ops.load_kubeconfig.return_value = "kubeconfig-content"

        self.service.import_kubeconfig("cluster-1", "/tmp/config")

        self.mock_ops.load_kubeconfig.assert_called_once_with(cluster_id="cluster-1")
        self.mock_file_writer.write_file.assert_called_once()

    def test_deploy_cluster_success(self):
        # Setup
        deploy_req = ClusterDeployRequest(
            name="new-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=["node-1"],
            control_plane_nodes=[],
        )

        self.mock_provider.list_available_nodes.return_value = [self.node1]
        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[], issues=[]
        )
        self.mock_repo.create.return_value = "cluster-new"
        self.mock_ops.deploy.return_value = "cluster-new"

        deployed_cluster = Cluster(
            id="cluster-new",
            name="new-cluster",
            status=ClusterStatus.READY,
            type=ClusterType.REMOTE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            nodes=[self.node1],
        )
        self.mock_repo.get.return_value = deployed_cluster

        # Execute
        result = self.service.deploy_cluster(deploy_req)

        # Verify
        self.assertIsInstance(result, DeployClusterResult)
        self.assertTrue(result.is_success)
        self.assertEqual(result.deployed_cluster.id, "cluster-new")
        self.mock_repo.create.assert_called_once()
        self.mock_ops.deploy.assert_called_once_with(cluster_id="cluster-new")

    def test_deploy_cluster_with_node_import(self):
        # Setup
        node_spec = ClusterNodeSpecification(
            hostname="host2",
            endpoint="1.2.3.5",
            username="user",
            ssh_key="key2",
            role=ClusterNodeRole.WORKER,
        )
        deploy_req = ClusterDeployRequest(
            name="import-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=[node_spec],
        )

        imported_node = ClusterNode(
            id="node-2",
            role=ClusterNodeRole.WORKER,
            hostname="host2",
            username="user",
            ssh_key_id="key2",
            status=ClusterNodeStatus.AVAILABLE,
            endpoint="1.2.3.5",
            free_resources=self.resources,
            occupied_resources=self.resources,
        )

        self.mock_provider.list_available_nodes.return_value = []
        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[imported_node], issues=[]
        )
        self.mock_repo.create.return_value = "cluster-import"
        self.mock_ops.deploy.return_value = "cluster-import"

        deployed_cluster = Cluster(
            id="cluster-import",
            name="import-cluster",
            status=ClusterStatus.READY,
            type=ClusterType.REMOTE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            nodes=[imported_node],
        )
        self.mock_repo.get.return_value = deployed_cluster

        # Execute
        result = self.service.deploy_cluster(deploy_req)

        # Verify
        self.assertTrue(result.is_success)
        self.mock_provider.import_nodes.assert_called_once()
        self.assertEqual(len(result.deployed_cluster.nodes), 1)

    def test_deploy_cluster_with_missing_nodes_and_issues(self):
        deploy_req = ClusterDeployRequest(
            name="fail-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=["missing-node"],
            control_plane_nodes=[],
        )

        self.mock_provider.list_available_nodes.return_value = []
        # import result returns issues
        spec = ClusterNodeSpecification(
            hostname="host2",
            endpoint="1.2.3.5",
            username="user",
            ssh_key="key2",
            role=ClusterNodeRole.WORKER,
        )
        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[],
            issues=[
                ClusterNodeImportIssue(
                    node_specification=spec, error_message="Import failed"
                )
            ],
        )

        result = self.service.deploy_cluster(deploy_req)

        # Should return result with issues and no cluster deployed because no valid nodes
        self.assertFalse(result.is_success)
        self.assertIsNone(result.deployed_cluster)
        self.assertEqual(
            len(result.issues), 1
        )  # one missing node + 0 imported issues (actually we didn't pass specs)

        # Let's test again with import failure
        deploy_req_import = ClusterDeployRequest(
            name="fail-import-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=[spec],
        )

        result_import = self.service.deploy_cluster(deploy_req_import)
        self.assertFalse(result_import.is_success)
        self.assertIsNone(result_import.deployed_cluster)
        self.assertEqual(len(result_import.issues), 1)
        self.assertIn("Import failed", result_import.issues[0].error_message)

    @patch("exls.clusters.core.service.poll_until")
    def test_deploy_cluster_polling(self, mock_poll_until: Mock):
        # Setup: node is in DISCOVERING state initially
        discovering_node = self.node1.model_copy(
            update={"status": ClusterNodeStatus.DISCOVERING}
        )
        self.mock_provider.list_available_nodes.side_effect = [
            [discovering_node],  # initial list
            [self.node1],  # after polling (mocked)
        ]

        mock_poll_until.return_value = [self.node1]

        deploy_req = ClusterDeployRequest(
            name="polling-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=["node-1"],
        )

        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[], issues=[]
        )
        self.mock_repo.create.return_value = "cluster-poll"
        self.mock_ops.deploy.return_value = "cluster-poll"

        deployed_cluster = Cluster(
            id="cluster-poll",
            name="polling-cluster",
            status=ClusterStatus.READY,
            type=ClusterType.REMOTE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            nodes=[self.node1],
        )
        self.mock_repo.get.return_value = deployed_cluster

        result = self.service.deploy_cluster(deploy_req)

        self.assertTrue(result.is_success)
        mock_poll_until.assert_called_once()

    @patch("exls.clusters.core.service.poll_until")
    def test_deploy_cluster_polling_control_plane(self, mock_poll_until: Mock):
        cp_node = self.node1.model_copy(
            update={"id": "cp-1", "role": ClusterNodeRole.CONTROL_PLANE}
        )
        discovering_cp_node = cp_node.model_copy(
            update={"status": ClusterNodeStatus.DISCOVERING}
        )

        self.mock_provider.list_available_nodes.side_effect = [
            [discovering_cp_node],
            [cp_node],
        ]
        mock_poll_until.return_value = [cp_node]

        deploy_req = ClusterDeployRequest(
            name="cp-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=[],
            control_plane_nodes=["cp-1"],
        )

        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[], issues=[]
        )
        self.mock_repo.create.return_value = "cluster-cp"
        self.mock_ops.deploy.return_value = "cluster-cp"

        deployed_cluster = Cluster(
            id="cluster-cp",
            name="cp-cluster",
            status=ClusterStatus.READY,
            type=ClusterType.REMOTE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            nodes=[cp_node],
        )
        self.mock_repo.get.return_value = deployed_cluster

        result = self.service.deploy_cluster(deploy_req)

        self.assertTrue(result.is_success)
        self.assertEqual(len(result.deployed_cluster.nodes), 1)
        self.assertEqual(
            result.deployed_cluster.nodes[0].role, ClusterNodeRole.CONTROL_PLANE
        )

    @patch("exls.clusters.core.service.poll_until")
    def test_deploy_cluster_polling_timeout(self, mock_poll_until: Mock):
        from exls.shared.core.polling import PollingTimeoutError

        discovering_node = self.node1.model_copy(
            update={"status": ClusterNodeStatus.DISCOVERING}
        )
        self.mock_provider.list_available_nodes.side_effect = [
            [discovering_node],
            [discovering_node],  # fetch after timeout still returns discovering
        ]

        mock_poll_until.side_effect = PollingTimeoutError("Timeout")

        deploy_req = ClusterDeployRequest(
            name="timeout-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=["node-1"],
        )

        # Validation happens before polling logic for existing nodes
        # If node is discovering, it goes to poll list.
        # Then _wait_for_nodes is called.

        result = self.service.deploy_cluster(deploy_req)

        # It should fail because nodes are not ready
        self.assertFalse(result.is_success)
        self.assertEqual(len(result.issues), 1)
        self.assertIn("Timed out", result.issues[0].error_message)

    def test_get_dashboard_url_unknown_status(self):
        unknown_cluster = self.cluster1.model_copy(
            update={"status": ClusterStatus.UNKNOWN}
        )
        self.mock_repo.get.return_value = unknown_cluster

        with self.assertRaises(ServiceError) as cm:
            self.service.get_dashboard_url("cluster-1")
        self.assertIn("unknown status", str(cm.exception))

    def test_scale_up_cluster(self):
        self.mock_repo.get.return_value = self.cluster1

        node2 = ClusterNode(
            id="node-2",
            role=ClusterNodeRole.WORKER,
            hostname="host2",
            username="user",
            ssh_key_id="key2",
            status=ClusterNodeStatus.AVAILABLE,
            endpoint="1.2.3.5",
            free_resources=self.resources,
            occupied_resources=self.resources,
        )
        self.mock_provider.list_available_nodes.return_value = [self.node1, node2]

        self.mock_ops.scale_up.return_value = ClusterScaleResult(
            nodes=[node2], issues=[]
        )

        result = self.service.scale_up_cluster("cluster-1", ["node-2"])

        self.assertEqual(len(result.nodes), 1)
        self.assertEqual(result.nodes[0].id, "node-2")
        self.mock_ops.scale_up.assert_called_once()

    def test_scale_up_cluster_invalid_node(self):
        self.mock_repo.get.return_value = self.cluster1
        self.mock_provider.list_available_nodes.return_value = [self.node1]

        result = self.service.scale_up_cluster("cluster-1", ["invalid-node"])

        self.assertEqual(len(result.issues), 1)
        self.assertIn("not found in available nodes", result.issues[0].error_message)
        self.mock_ops.scale_up.assert_not_called()

    def test_remove_nodes_from_cluster(self):
        self.mock_repo.get.return_value = self.cluster1

        self.mock_ops.scale_down.return_value = ClusterScaleResult(
            nodes=[self.node1], issues=[]
        )

        result = self.service.remove_nodes_from_cluster("cluster-1", ["node-1"])

        self.assertEqual(len(result.nodes), 1)
        self.assertEqual(result.nodes[0].id, "node-1")
        self.mock_ops.scale_down.assert_called_once()

    def test_remove_nodes_from_cluster_invalid_node(self):
        self.mock_repo.get.return_value = self.cluster1
        # No need to mock return value of scale_down as it shouldn't be called

        result = self.service.remove_nodes_from_cluster("cluster-1", ["invalid-node"])

        self.assertEqual(len(result.issues), 1)
        self.assertIn("not part of the cluster", result.issues[0].error_message)
        self.mock_ops.scale_down.assert_not_called()

    def test_deploy_cluster_partial_success(self):
        # Setup: 1 valid node, 1 invalid node
        deploy_req = ClusterDeployRequest(
            name="partial-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=["node-1", "missing-node"],
        )

        self.mock_provider.list_available_nodes.return_value = [self.node1]
        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[], issues=[]
        )

        self.mock_repo.create.return_value = "cluster-partial"
        self.mock_ops.deploy.return_value = "cluster-partial"

        deployed_cluster = self.cluster1.model_copy(update={"id": "cluster-partial"})
        self.mock_repo.get.return_value = deployed_cluster

        result = self.service.deploy_cluster(deploy_req)

        # It is technically a partial success, but checking result objects:
        self.assertIsNotNone(result.deployed_cluster)
        self.assertEqual(len(result.issues), 1)
        self.assertIn("not found", result.issues[0].error_message)
        self.assertEqual(len(result.deployed_cluster.nodes), 1)

    def test_deploy_cluster_with_failed_node(self):
        # Setup: Node in FAILED status should be reported as issue
        failed_node = self.node1.model_copy(update={"status": ClusterNodeStatus.FAILED})

        deploy_req = ClusterDeployRequest(
            name="failed-node-cluster",
            type=ClusterType.REMOTE,
            enable_vpn=False,
            enable_telemetry=False,
            enable_multinode_training=False,
            prepare_llm_inference_environment=False,
            worker_nodes=["node-1"],
        )

        self.mock_provider.list_available_nodes.return_value = [failed_node]
        self.mock_provider.import_nodes.return_value = ClusterNodesImportResult(
            nodes=[], issues=[]
        )

        result = self.service.deploy_cluster(deploy_req)

        self.assertFalse(result.is_success)
        self.assertIsNone(result.deployed_cluster)
        self.assertEqual(len(result.issues), 1)
        self.assertIn("invalid status", result.issues[0].error_message)

    def test_list_available_nodes(self):
        self.mock_provider.list_available_nodes.return_value = [self.node1]

        result = self.service.list_available_nodes()

        self.assertEqual(result, [self.node1])
        self.mock_provider.list_available_nodes.assert_called_once()
