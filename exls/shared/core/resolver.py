from __future__ import annotations

import uuid
from typing import List, Optional, Protocol, Sequence, TypeVar


class NamedResource(Protocol):
    """Protocol for resources that have an id and a name."""

    @property
    def id(self) -> str: ...

    @property
    def name(self) -> str: ...


T = TypeVar("T", bound=NamedResource)


def is_uuid(value: str) -> bool:
    """Check if a string looks like a UUID."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


class ResourceNotFoundError(Exception):
    """Raised when a resource cannot be found by name or ID."""

    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(f"No {resource_type} found with name or ID '{identifier}'")


class AmbiguousResourceError(Exception):
    """Raised when multiple resources match the given name."""

    def __init__(self, resource_type: str, name: str, matches: Sequence[NamedResource]):
        self.resource_type = resource_type
        self.name = name
        self.matches = matches
        ids_str = ", ".join(f"'{m.id}'" for m in matches)
        super().__init__(
            f"Multiple {resource_type}s found with name '{name}'. "
            f"Please use one of the following IDs: {ids_str}"
        )


def _check_id(
    resources: List[T],
    identifier: str,
) -> Optional[str]:
    """
    Check if the identifier matches a resource ID exactly.

    Args:
        resources: List of resources to search through
        identifier: The identifier to match against resource IDs

    Returns:
        The resource ID if exactly one match is found, None otherwise.
    """
    id_matches = [r for r in resources if r.id == identifier]
    if len(id_matches) == 1:
        return id_matches[0].id
    return None


def _check_names(
    resources: List[T],
    name: str,
    resource_type: str,
) -> str:
    """
    Check if the name matches a resource name.

    Resolution order:
        1. Exact name match (case-sensitive)
        2. Case-insensitive name match

    Case-insensitive matching is a UX convenience. Resource names are stored as
    lowercase (Kubernetes constraint), so only one case variant can exist in the
    backend. This allows users to type e.g. "My-Cluster" to resolve "my-cluster".

    Args:
        resources: List of resources to search through
        name: The name to match against resource names
        resource_type: Human-readable resource type for error messages

    Returns:
        The resource ID if a unique match is found.

    Raises:
        ResourceNotFoundError: If no resource matches the name
        AmbiguousResourceError: If multiple resources match the name
    """
    # Exact name match (case-sensitive)
    name_matches = [r for r in resources if r.name == name]
    if len(name_matches) == 1:
        return name_matches[0].id
    if len(name_matches) > 1:
        raise AmbiguousResourceError(resource_type, name, name_matches)

    # Case-insensitive name match
    name_lower = name.lower()
    name_matches_ci = [r for r in resources if r.name.lower() == name_lower]
    if len(name_matches_ci) == 1:
        return name_matches_ci[0].id
    if len(name_matches_ci) > 1:
        raise AmbiguousResourceError(resource_type, name, name_matches_ci)

    # No match found
    raise ResourceNotFoundError(resource_type, name)


def resolve_resource_id(
    resources: List[T],
    name_or_id: str,
    resource_type: str,
) -> str:
    """
    Resolve a resource name or ID to an ID.

    Resolution strategy:
        - If input is a UUID: ID matching
        - Otherwise: name matching

    Args:
        resources: List of resources to search through
        name_or_id: Either a resource ID or name
        resource_type: Human-readable resource type for error messages (e.g., "cluster")

    Returns:
        The resource ID

    Raises:
        ResourceNotFoundError: If no resource matches the name or ID
        AmbiguousResourceError: If multiple resources match the name
    """
    if is_uuid(name_or_id):
        matched_id = _check_id(resources, name_or_id)
        if matched_id is None:
            raise ResourceNotFoundError(resource_type, name_or_id)
        return matched_id

    return _check_names(resources, name_or_id, resource_type)


def find_resource_by_name_or_id(
    resources: List[T],
    name_or_id: str,
    resource_type: str,
) -> T:
    """
    Find a resource by name or ID.

    Args:
        resources: List of resources to search through
        name_or_id: Either a resource ID or name
        resource_type: Human-readable resource type for error messages

    Returns:
        The matching resource

    Raises:
        ResourceNotFoundError: If no resource matches the name or ID
        AmbiguousResourceError: If multiple resources match the name
    """
    resource_id = resolve_resource_id(resources, name_or_id, resource_type)
    for resource in resources:
        if resource.id == resource_id:
            return resource
    raise ResourceNotFoundError(resource_type, name_or_id)
