from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, create_autospec

import pytest

from exls.nodes.core.domain import (
    CloudNode,
    NodeResources,
    NodeStatus,
    SelfManagedNode,
)
from exls.nodes.core.ports.operations import NodesOperations
from exls.nodes.core.ports.provider import NodeSshKey, SshKeyProvider
from exls.nodes.core.ports.repository import NodesRepository
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
    NodesSshKeySpecification,
)
from exls.nodes.core.results import DeleteNodesResult, ImportSelfmanagedNodesResult
from exls.nodes.core.service import NodesService
from exls.shared.core.exceptions import ServiceError


@pytest.fixture
def mock_nodes_repository() -> MagicMock:
    return create_autospec(NodesRepository)


@pytest.fixture
def mock_nodes_operations() -> MagicMock:
    return create_autospec(NodesOperations)


@pytest.fixture
def mock_ssh_key_provider() -> MagicMock:
    return create_autospec(SshKeyProvider)


@pytest.fixture
def nodes_service(
    mock_nodes_repository: MagicMock,
    mock_nodes_operations: MagicMock,
    mock_ssh_key_provider: MagicMock,
) -> NodesService:
    return NodesService(
        nodes_repository=mock_nodes_repository,
        nodes_operations=mock_nodes_operations,
        ssh_key_provider=mock_ssh_key_provider,
    )


@pytest.fixture
def sample_resources() -> NodeResources:
    return NodeResources(
        gpu_type="nvidia-a100",
        gpu_vendor="nvidia",
        gpu_count=1,
        cpu_cores=16,
        memory_gb=64,
        storage_gb=100,
    )


@pytest.fixture
def sample_self_managed_node(sample_resources: NodeResources) -> SelfManagedNode:
    return SelfManagedNode(
        id="node-1",
        hostname="host1",
        import_time=datetime.now(),
        status=NodeStatus.AVAILABLE,
        resources=sample_resources,
        ssh_key_id="key-1",
        username="user",
        endpoint="1.2.3.4",
    )


@pytest.fixture
def sample_cloud_node(sample_resources: NodeResources) -> CloudNode:
    return CloudNode(
        id="node-cloud-1",
        hostname="cloud-host1",
        import_time=datetime.now(),
        status=NodeStatus.AVAILABLE,
        resources=sample_resources,
        provider="aws",
        instance_type="p3.2xlarge",
        price_per_hour="3.06",
    )


@pytest.fixture
def sample_ssh_key() -> NodeSshKey:
    return NodeSshKey(id="key-1", name="my-key")


class TestNodesService:
    def test_list_nodes(
        self,
        nodes_service: NodesService,
        mock_nodes_repository: MagicMock,
        mock_ssh_key_provider: MagicMock,
        sample_self_managed_node: SelfManagedNode,
        sample_ssh_key: NodeSshKey,
    ) -> None:
        # Arrange
        mock_nodes_repository.list.return_value = [sample_self_managed_node]
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]

        # Act
        result = nodes_service.list_nodes()

        # Assert
        assert len(result) == 1
        assert result[0].id == sample_self_managed_node.id
        assert result[0].ssh_key_name == sample_ssh_key.name
        mock_nodes_repository.list.assert_called_once_with(filter=None)
        mock_ssh_key_provider.list_keys.assert_called_once()

    def test_list_nodes_with_filter(
        self,
        nodes_service: NodesService,
        mock_nodes_repository: MagicMock,
        mock_ssh_key_provider: MagicMock,
    ) -> None:
        # Arrange
        filter_criteria = NodesFilterCriteria(status=NodeStatus.AVAILABLE)
        mock_nodes_repository.list.return_value = []
        mock_ssh_key_provider.list_keys.return_value = []

        # Act
        nodes_service.list_nodes(filter=filter_criteria)

        # Assert
        mock_nodes_repository.list.assert_called_once_with(filter=filter_criteria)

    def test_get_node(
        self,
        nodes_service: NodesService,
        mock_nodes_repository: MagicMock,
        mock_ssh_key_provider: MagicMock,
        sample_self_managed_node: SelfManagedNode,
        sample_ssh_key: NodeSshKey,
    ) -> None:
        # Arrange
        mock_nodes_repository.get.return_value = sample_self_managed_node
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]

        # Act
        result = nodes_service.get_node("node-1")

        # Assert
        assert result.id == "node-1"
        assert result.ssh_key_name == "my-key"
        mock_nodes_repository.get.assert_called_once_with("node-1")

    def test_delete_nodes(
        self, nodes_service: NodesService, mock_nodes_repository: MagicMock
    ) -> None:
        # Arrange
        node_ids = ["node-1", "node-2"]

        def return_arg(x: str) -> str:
            return x

        mock_nodes_repository.delete.side_effect = return_arg

        # Act
        result = nodes_service.delete_nodes(node_ids)

        # Assert
        assert isinstance(result, DeleteNodesResult)
        assert set(result.deleted_node_ids) == set(node_ids)
        assert result.issues == []
        assert mock_nodes_repository.delete.call_count == 2

    def test_delete_nodes_partial_failure(
        self, nodes_service: NodesService, mock_nodes_repository: MagicMock
    ) -> None:
        # Arrange
        node_ids = ["node-1", "node-2"]

        def delete_side_effect(node_id: str) -> str:
            if node_id == "node-2":
                raise Exception("Failed to delete")
            return node_id

        mock_nodes_repository.delete.side_effect = delete_side_effect

        # Act
        result = nodes_service.delete_nodes(node_ids)

        # Assert
        assert "node-1" in result.deleted_node_ids
        assert result.issues is not None
        assert len(result.issues) == 1
        assert result.issues[0].node_id == "node-2"
        assert "Failed to delete" in result.issues[0].error_message

    def test_list_ssh_keys(
        self,
        nodes_service: NodesService,
        mock_ssh_key_provider: MagicMock,
        sample_ssh_key: NodeSshKey,
    ) -> None:
        # Arrange
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]

        # Act
        result = nodes_service.list_ssh_keys()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_ssh_key
        mock_ssh_key_provider.list_keys.assert_called_once()

    def test_import_cloud_nodes(
        self,
        nodes_service: NodesService,
        mock_nodes_repository: MagicMock,
        mock_nodes_operations: MagicMock,
        sample_cloud_node: CloudNode,
    ) -> None:
        # Arrange
        request = ImportCloudNodeRequest(
            hostname="cloud-host", offer_id="offer-1", amount=1
        )
        mock_nodes_operations.import_cloud_nodes.return_value = ["node-cloud-1"]
        mock_nodes_repository.get.return_value = sample_cloud_node

        # Act
        result = nodes_service.import_cloud_nodes(request)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_cloud_node
        mock_nodes_operations.import_cloud_nodes.assert_called_once_with(
            parameters=request
        )
        mock_nodes_repository.get.assert_called_once_with("node-cloud-1")

    def test_import_selfmanaged_nodes_empty(self, nodes_service: NodesService) -> None:
        # Act & Assert
        with pytest.raises(ServiceError, match="must contain at least one node"):
            nodes_service.import_selfmanaged_nodes([])

    def test_import_selfmanaged_nodes_success(
        self,
        nodes_service: NodesService,
        mock_nodes_operations: MagicMock,
        mock_ssh_key_provider: MagicMock,
        mock_nodes_repository: MagicMock,
        sample_ssh_key: NodeSshKey,
        sample_self_managed_node: SelfManagedNode,
    ) -> None:
        # Arrange
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key="key-1",
        )
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]
        mock_nodes_operations.import_selfmanaged_node.return_value = "node-1"
        mock_nodes_repository.get.return_value = sample_self_managed_node

        # Act
        result = nodes_service.import_selfmanaged_nodes([request])

        # Assert
        assert isinstance(result, ImportSelfmanagedNodesResult)
        assert len(result.imported_nodes) == 1
        assert result.imported_nodes[0].id == "node-1"
        assert len(result.issues) == 0

    def test_import_selfmanaged_nodes_with_new_key(
        self,
        nodes_service: NodesService,
        mock_nodes_operations: MagicMock,
        mock_ssh_key_provider: MagicMock,
        mock_nodes_repository: MagicMock,
        sample_ssh_key: NodeSshKey,
        sample_self_managed_node: SelfManagedNode,
    ) -> None:
        # Arrange
        key_spec = NodesSshKeySpecification(name="new-key", key_path=Path("/tmp/key"))
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key=key_spec,
        )

        # Initial list keys (empty or irrelevant)
        mock_ssh_key_provider.list_keys.return_value = []

        # Mock import key
        new_key = NodeSshKey(id="new-key-id", name="new-key")
        mock_ssh_key_provider.import_key.return_value = new_key

        mock_nodes_operations.import_selfmanaged_node.return_value = "node-1"

        # Return node with new key
        node_with_new_key = sample_self_managed_node.model_copy()
        node_with_new_key.ssh_key_id = "new-key-id"
        mock_nodes_repository.get.return_value = node_with_new_key

        # Act
        result = nodes_service.import_selfmanaged_nodes([request])

        # Assert
        assert len(result.imported_nodes) == 1
        assert len(result.issues) == 0
        mock_ssh_key_provider.import_key.assert_called_once_with(
            name="new-key", key_path=Path("/tmp/key")
        )

    def test_import_selfmanaged_nodes_invalid_key_id(
        self,
        nodes_service: NodesService,
        mock_ssh_key_provider: MagicMock,
    ) -> None:
        # Arrange
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key="invalid-key-id",
        )
        mock_ssh_key_provider.list_keys.return_value = []

        # Act
        result = nodes_service.import_selfmanaged_nodes([request])

        # Assert
        assert len(result.imported_nodes) == 0
        assert len(result.issues) == 1
        assert (
            "SSH key with ID invalid-key-id not found" in result.issues[0].error_message
        )

    def test_import_selfmanaged_nodes_key_import_failure(
        self,
        nodes_service: NodesService,
        mock_ssh_key_provider: MagicMock,
    ) -> None:
        # Arrange
        key_spec = NodesSshKeySpecification(name="bad-key", key_path=Path("/tmp/key"))
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key=key_spec,
        )
        mock_ssh_key_provider.list_keys.return_value = []
        mock_ssh_key_provider.import_key.side_effect = Exception("Key import failed")

        # Act
        result = nodes_service.import_selfmanaged_nodes([request])

        # Assert
        assert len(result.imported_nodes) == 0
        assert len(result.issues) == 1
        assert "Key import failed" in result.issues[0].error_message

    def test_import_selfmanaged_nodes_wait_success(
        self,
        nodes_service: NodesService,
        mock_nodes_operations: MagicMock,
        mock_ssh_key_provider: MagicMock,
        mock_nodes_repository: MagicMock,
        sample_ssh_key: NodeSshKey,
        sample_self_managed_node: SelfManagedNode,
    ) -> None:
        # Arrange
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key="key-1",
        )
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]
        mock_nodes_operations.import_selfmanaged_node.return_value = "node-1"

        # Mock polling behavior
        deploying_node = sample_self_managed_node.model_copy()
        deploying_node.status = NodeStatus.DISCOVERING

        deployed_node = sample_self_managed_node.model_copy()
        deployed_node.status = NodeStatus.DEPLOYED

        mock_nodes_repository.get.side_effect = [deploying_node, deployed_node]

        # Act
        result = nodes_service.import_selfmanaged_nodes(
            [request], wait_for_available=True
        )

        # Assert
        assert len(result.imported_nodes) == 1
        assert result.imported_nodes[0].status == NodeStatus.DEPLOYED

    def test_import_selfmanaged_nodes_wait_failure(
        self,
        nodes_service: NodesService,
        mock_nodes_operations: MagicMock,
        mock_ssh_key_provider: MagicMock,
        mock_nodes_repository: MagicMock,
        sample_ssh_key: NodeSshKey,
        sample_self_managed_node: SelfManagedNode,
    ) -> None:
        # Arrange
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key="key-1",
        )
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]
        mock_nodes_operations.import_selfmanaged_node.return_value = "node-1"

        failed_node = sample_self_managed_node.model_copy()
        failed_node.status = NodeStatus.FAILED
        mock_nodes_repository.get.return_value = failed_node

        # Act
        result = nodes_service.import_selfmanaged_nodes(
            [request], wait_for_available=True
        )

        # Assert
        assert len(result.imported_nodes) == 0
        assert len(result.issues) == 1
        assert "failed with status: FAILED" in result.issues[0].error_message

    def test_import_selfmanaged_nodes_wrong_return_type(
        self,
        nodes_service: NodesService,
        mock_nodes_operations: MagicMock,
        mock_ssh_key_provider: MagicMock,
        mock_nodes_repository: MagicMock,
        sample_ssh_key: NodeSshKey,
        sample_cloud_node: CloudNode,
    ) -> None:
        # Arrange
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key="key-1",
        )
        mock_ssh_key_provider.list_keys.return_value = [sample_ssh_key]
        mock_nodes_operations.import_selfmanaged_node.return_value = "node-1"

        # Return a CloudNode instead of SelfManagedNode
        mock_nodes_repository.get.return_value = sample_cloud_node

        # Act
        result = nodes_service.import_selfmanaged_nodes([request])

        # Assert
        assert len(result.imported_nodes) == 0
        assert len(result.issues) == 1
        assert "returned unexpected type" in result.issues[0].error_message

    def test_import_selfmanaged_nodes_existing_key_name_idempotency(
        self,
        nodes_service: NodesService,
        mock_nodes_operations: MagicMock,
        mock_ssh_key_provider: MagicMock,
        mock_nodes_repository: MagicMock,
        sample_ssh_key: NodeSshKey,
        sample_self_managed_node: SelfManagedNode,
    ) -> None:
        # Arrange
        # Key exists in provider with name "existing-key"
        existing_key = NodeSshKey(id="existing-id", name="existing-key")
        mock_ssh_key_provider.list_keys.return_value = [existing_key]

        # Request provides spec with SAME name "existing-key"
        key_spec = NodesSshKeySpecification(
            name="existing-key", key_path=Path("/tmp/key")
        )
        request = ImportSelfmanagedNodeRequest(
            hostname="host1",
            endpoint="1.2.3.4",
            username="user",
            ssh_key=key_spec,
        )

        mock_nodes_operations.import_selfmanaged_node.return_value = "node-1"
        mock_nodes_repository.get.return_value = sample_self_managed_node

        # Act
        result = nodes_service.import_selfmanaged_nodes([request])

        # Assert
        # Should NOT call import_key because name exists
        mock_ssh_key_provider.import_key.assert_not_called()

        # Should proceed to import node using the EXISTING key ID
        assert len(result.imported_nodes) == 1
        # Verify call arguments to ensure correct ID was resolved
        call_args = mock_nodes_operations.import_selfmanaged_node.call_args
        assert call_args[1]["parameters"].ssh_key_id == "existing-id"

    def test_list_nodes_mixed_types_and_missing_keys(
        self,
        nodes_service: NodesService,
        mock_nodes_repository: MagicMock,
        mock_ssh_key_provider: MagicMock,
        sample_self_managed_node: SelfManagedNode,
        sample_cloud_node: CloudNode,
    ) -> None:
        # Arrange
        # Node 1: SelfManaged, Key ID "key-1" (Exists)
        node1 = sample_self_managed_node.model_copy()
        node1.ssh_key_id = "key-1"

        # Node 2: SelfManaged, Key ID "key-missing" (Does not exist in provider)
        node2 = sample_self_managed_node.model_copy()
        node2.ssh_key_id = "key-missing"
        node2.id = "node-2"

        # Node 3: CloudNode (Should be skipped by key resolver)
        node3 = sample_cloud_node

        mock_nodes_repository.list.return_value = [node1, node2, node3]

        # Provider only has key-1
        mock_ssh_key_provider.list_keys.return_value = [
            NodeSshKey(id="key-1", name="Key One")
        ]

        # Act
        result = nodes_service.list_nodes()

        # Assert
        assert len(result) == 3

        # Node 1: Resolved
        assert result[0].id == "node-1"
        assert isinstance(result[0], SelfManagedNode)
        assert result[0].ssh_key_name == "Key One"

        # Node 2: Not resolved (kept default/empty), no crash
        assert result[1].id == "node-2"
        assert isinstance(result[1], SelfManagedNode)
        # Assuming default is "" or None based on domain definition
        assert not result[1].ssh_key_name

        # Node 3: CloudNode untouched
        assert result[2].id == "node-cloud-1"
        assert isinstance(result[2], CloudNode)
