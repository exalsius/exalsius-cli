"""Tests for the resource name-or-id resolver."""

from typing import List

import pytest
from pydantic import BaseModel

from exls.shared.core.resolver import (
    AmbiguousResourceError,
    ResourceNotFoundError,
    find_resource_by_name_or_id,
    is_uuid,
    resolve_resource_id,
)


class MockResource(BaseModel):
    """Mock resource for testing."""

    id: str
    name: str


class TestIsUuid:
    """Tests for the is_uuid function."""

    def test_valid_uuid_lowercase(self):
        assert is_uuid("550e8400-e29b-41d4-a716-446655440000") is True

    def test_valid_uuid_uppercase(self):
        assert is_uuid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_valid_uuid_mixed_case(self):
        assert is_uuid("550e8400-E29B-41d4-A716-446655440000") is True

    def test_invalid_uuid_too_short(self):
        assert is_uuid("550e8400-e29b-41d4-a716") is False

    def test_valid_uuid_no_dashes(self):
        # Python's uuid.UUID() accepts UUIDs without dashes
        assert is_uuid("550e8400e29b41d4a716446655440000") is True

    def test_invalid_uuid_wrong_format(self):
        assert is_uuid("not-a-uuid-at-all") is False

    def test_empty_string(self):
        assert is_uuid("") is False

    def test_regular_name(self):
        assert is_uuid("my-cluster") is False
        assert is_uuid("jupyter-workspace-123") is False


class TestResolveResourceId:
    """Tests for the resolve_resource_id function."""

    @pytest.fixture
    def resources(self) -> List[MockResource]:
        return [
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440001", name="cluster-alpha"
            ),
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440002", name="cluster-beta"
            ),
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440003", name="cluster-gamma"
            ),
        ]

    def test_resolve_by_exact_id(self, resources: List[MockResource]) -> None:
        result = resolve_resource_id(
            resources, "550e8400-e29b-41d4-a716-446655440002", "cluster"
        )
        assert result == "550e8400-e29b-41d4-a716-446655440002"

    def test_resolve_by_exact_name(self, resources: List[MockResource]) -> None:
        result = resolve_resource_id(resources, "cluster-beta", "cluster")
        assert result == "550e8400-e29b-41d4-a716-446655440002"

    def test_resolve_by_name_case_insensitive(
        self, resources: List[MockResource]
    ) -> None:
        result = resolve_resource_id(resources, "CLUSTER-BETA", "cluster")
        assert result == "550e8400-e29b-41d4-a716-446655440002"

    def test_resolve_by_name_mixed_case(self, resources: List[MockResource]) -> None:
        result = resolve_resource_id(resources, "Cluster-Beta", "cluster")
        assert result == "550e8400-e29b-41d4-a716-446655440002"

    def test_not_found_by_name(self, resources: List[MockResource]) -> None:
        with pytest.raises(ResourceNotFoundError) as exc_info:
            resolve_resource_id(resources, "cluster-delta", "cluster")
        assert exc_info.value.resource_type == "cluster"
        assert exc_info.value.identifier == "cluster-delta"
        assert "No cluster found" in str(exc_info.value)

    def test_not_found_by_id(self, resources: List[MockResource]) -> None:
        with pytest.raises(ResourceNotFoundError) as exc_info:
            resolve_resource_id(
                resources, "550e8400-e29b-41d4-a716-999999999999", "cluster"
            )
        assert "No cluster found" in str(exc_info.value)

    def test_ambiguous_name_exact_match(self):
        resources = [
            MockResource(id="id-1", name="my-cluster"),
            MockResource(id="id-2", name="my-cluster"),
        ]
        with pytest.raises(AmbiguousResourceError) as exc_info:
            resolve_resource_id(resources, "my-cluster", "cluster")
        assert exc_info.value.resource_type == "cluster"
        assert exc_info.value.name == "my-cluster"
        assert len(exc_info.value.matches) == 2
        assert "Multiple clusters found" in str(exc_info.value)
        assert "'id-1'" in str(exc_info.value)
        assert "'id-2'" in str(exc_info.value)

    def test_ambiguous_name_case_insensitive(self):
        resources = [
            MockResource(id="id-1", name="My-Cluster"),
            MockResource(id="id-2", name="my-cluster"),
        ]
        with pytest.raises(AmbiguousResourceError) as exc_info:
            resolve_resource_id(resources, "MY-CLUSTER", "cluster")
        assert len(exc_info.value.matches) == 2

    def test_empty_resources_list(self):
        with pytest.raises(ResourceNotFoundError):
            resolve_resource_id([], "any-name", "cluster")

    def test_id_takes_precedence_over_name(self):
        """If a resource's ID matches the search term, use it even if another resource has that as its name."""
        resources = [
            MockResource(id="special-id", name="cluster-one"),
            MockResource(
                id="other-id", name="special-id"
            ),  # Name matches first resource's ID
        ]
        result = resolve_resource_id(resources, "special-id", "cluster")
        # Should return the resource with matching ID, not the one with matching name
        assert result == "special-id"

    def test_non_uuid_id_still_matches_by_id(self):
        """IDs don't have to be UUIDs - any exact ID match should work."""
        resources = [
            MockResource(id="simple-id-123", name="cluster-one"),
        ]
        result = resolve_resource_id(resources, "simple-id-123", "cluster")
        assert result == "simple-id-123"


class TestFindResourceByNameOrId:
    """Tests for the find_resource_by_name_or_id function."""

    @pytest.fixture
    def resources(self) -> List[MockResource]:
        return [
            MockResource(id="id-1", name="resource-alpha"),
            MockResource(id="id-2", name="resource-beta"),
        ]

    def test_find_by_id(self, resources: List[MockResource]) -> None:
        result = find_resource_by_name_or_id(resources, "id-1", "resource")
        assert result.id == "id-1"
        assert result.name == "resource-alpha"

    def test_find_by_name(self, resources: List[MockResource]) -> None:
        result = find_resource_by_name_or_id(resources, "resource-beta", "resource")
        assert result.id == "id-2"
        assert result.name == "resource-beta"

    def test_not_found(self, resources: List[MockResource]) -> None:
        with pytest.raises(ResourceNotFoundError):
            find_resource_by_name_or_id(resources, "nonexistent", "resource")

    def test_ambiguous(self) -> None:
        resources: List[MockResource] = [
            MockResource(id="id-1", name="duplicate"),
            MockResource(id="id-2", name="duplicate"),
        ]
        with pytest.raises(AmbiguousResourceError):
            find_resource_by_name_or_id(resources, "duplicate", "resource")


class TestRealWorldScenarios:
    """Tests simulating real-world usage patterns."""

    def test_kubernetes_style_names(self):
        """Test with typical Kubernetes-style resource names."""
        resources = [
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440001",
                name="jupyter-friendly-dolphin",
            ),
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440002",
                name="marimo-happy-penguin",
            ),
        ]
        result = resolve_resource_id(resources, "jupyter-friendly-dolphin", "workspace")
        assert result == "550e8400-e29b-41d4-a716-446655440001"

    def test_user_provides_partial_uuid_as_name(self):
        """If user provides something that looks like a partial UUID, treat it as a name."""
        resources = [
            MockResource(id="full-uuid-here", name="550e8400"),
        ]
        # This is not a valid UUID, so it should be treated as a name search
        result = resolve_resource_id(resources, "550e8400", "cluster")
        assert result == "full-uuid-here"

    def test_cluster_workspace_node_names(self):
        """Test with typical names for different resource types."""
        clusters = [
            MockResource(id="c1", name="production-cluster"),
            MockResource(id="c2", name="staging-cluster"),
        ]
        workspaces = [
            MockResource(id="w1", name="jupyter-data-analysis"),
            MockResource(id="w2", name="devpod-backend-dev"),
        ]
        nodes = [
            MockResource(id="n1", name="gpu-node-01"),
            MockResource(id="n2", name="gpu-node-02"),
        ]

        assert resolve_resource_id(clusters, "production-cluster", "cluster") == "c1"
        assert (
            resolve_resource_id(workspaces, "jupyter-data-analysis", "workspace")
            == "w1"
        )
        assert resolve_resource_id(nodes, "gpu-node-02", "node") == "n2"
