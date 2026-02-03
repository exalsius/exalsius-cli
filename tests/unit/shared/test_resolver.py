"""Tests for the resource name-or-id resolver."""

from typing import List

import pytest
from pydantic import BaseModel

from exls.shared.core.resolver import _check_id  # pyright: ignore[reportPrivateUsage]
from exls.shared.core.resolver import (
    _check_names,  # pyright: ignore[reportPrivateUsage]
)
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


class TestCheckId:
    """Tests for the _check_id helper function."""

    @pytest.fixture
    def resources(self) -> List[MockResource]:
        return [
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440001", name="cluster-alpha"
            ),
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440002", name="cluster-beta"
            ),
            MockResource(id="simple-id", name="cluster-gamma"),
        ]

    def test_returns_id_on_exact_uuid_match(
        self, resources: List[MockResource]
    ) -> None:
        result = _check_id(resources, "550e8400-e29b-41d4-a716-446655440001")
        assert result == "550e8400-e29b-41d4-a716-446655440001"

    def test_returns_id_on_exact_non_uuid_match(
        self, resources: List[MockResource]
    ) -> None:
        result = _check_id(resources, "simple-id")
        assert result == "simple-id"

    def test_returns_none_when_no_match(self, resources: List[MockResource]) -> None:
        result = _check_id(resources, "nonexistent-id")
        assert result is None

    def test_returns_none_for_empty_list(self) -> None:
        result = _check_id([], "any-id")
        assert result is None

    def test_does_not_match_by_name(self, resources: List[MockResource]) -> None:
        # Should not find anything when searching by name
        result = _check_id(resources, "cluster-alpha")
        assert result is None


class TestCheckNames:
    """Tests for the _check_names helper function."""

    @pytest.fixture
    def resources(self) -> List[MockResource]:
        return [
            MockResource(id="id-1", name="cluster-alpha"),
            MockResource(id="id-2", name="cluster-beta"),
            MockResource(id="id-3", name="cluster-gamma"),
        ]

    def test_returns_id_on_exact_name_match(
        self, resources: List[MockResource]
    ) -> None:
        result = _check_names(resources, "cluster-beta", "cluster")
        assert result == "id-2"

    def test_returns_id_on_case_insensitive_match(
        self, resources: List[MockResource]
    ) -> None:
        result = _check_names(resources, "CLUSTER-BETA", "cluster")
        assert result == "id-2"

    def test_returns_id_on_mixed_case_match(
        self, resources: List[MockResource]
    ) -> None:
        result = _check_names(resources, "Cluster-Beta", "cluster")
        assert result == "id-2"

    def test_raises_not_found_when_no_match(
        self, resources: List[MockResource]
    ) -> None:
        with pytest.raises(ResourceNotFoundError) as exc_info:
            _check_names(resources, "cluster-delta", "cluster")
        assert exc_info.value.resource_type == "cluster"
        assert exc_info.value.identifier == "cluster-delta"

    def test_raises_ambiguous_on_exact_duplicates(self) -> None:
        resources = [
            MockResource(id="id-1", name="my-cluster"),
            MockResource(id="id-2", name="my-cluster"),
        ]
        with pytest.raises(AmbiguousResourceError) as exc_info:
            _check_names(resources, "my-cluster", "cluster")
        assert exc_info.value.resource_type == "cluster"
        assert exc_info.value.name == "my-cluster"
        assert len(exc_info.value.matches) == 2

    def test_raises_ambiguous_on_case_insensitive_duplicates(self) -> None:
        resources = [
            MockResource(id="id-1", name="My-Cluster"),
            MockResource(id="id-2", name="my-cluster"),
        ]
        with pytest.raises(AmbiguousResourceError) as exc_info:
            _check_names(resources, "MY-CLUSTER", "cluster")
        assert len(exc_info.value.matches) == 2

    def test_prefers_exact_match_over_case_insensitive(self) -> None:
        """If there's an exact match, return it even if case-insensitive would match multiple."""
        resources = [
            MockResource(id="id-1", name="My-Cluster"),
            MockResource(id="id-2", name="my-cluster"),
        ]
        # Exact match for "my-cluster" should return id-2
        result = _check_names(resources, "my-cluster", "cluster")
        assert result == "id-2"

    def test_raises_not_found_for_empty_list(self) -> None:
        with pytest.raises(ResourceNotFoundError):
            _check_names([], "any-name", "cluster")


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


class TestFindResourceByNameOrId:
    """Tests for the find_resource_by_name_or_id function."""

    @pytest.fixture
    def resources(self) -> List[MockResource]:
        return [
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440001", name="resource-alpha"
            ),
            MockResource(
                id="550e8400-e29b-41d4-a716-446655440002", name="resource-beta"
            ),
        ]

    def test_find_by_id(self, resources: List[MockResource]) -> None:
        result = find_resource_by_name_or_id(
            resources, "550e8400-e29b-41d4-a716-446655440001", "resource"
        )
        assert result.id == "550e8400-e29b-41d4-a716-446655440001"
        assert result.name == "resource-alpha"

    def test_find_by_name(self, resources: List[MockResource]) -> None:
        result = find_resource_by_name_or_id(resources, "resource-beta", "resource")
        assert result.id == "550e8400-e29b-41d4-a716-446655440002"
        assert result.name == "resource-beta"

    def test_not_found(self, resources: List[MockResource]) -> None:
        with pytest.raises(ResourceNotFoundError):
            find_resource_by_name_or_id(resources, "nonexistent", "resource")

    def test_ambiguous(self) -> None:
        resources: List[MockResource] = [
            MockResource(id="550e8400-e29b-41d4-a716-446655440001", name="duplicate"),
            MockResource(id="550e8400-e29b-41d4-a716-446655440002", name="duplicate"),
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
