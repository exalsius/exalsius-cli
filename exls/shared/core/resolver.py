"""Utilities for resolving resource names or IDs to IDs."""

from __future__ import annotations

import uuid
from typing import List, Protocol, Sequence, TypeVar


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


def resolve_resource_id(
    resources: List[T],
    name_or_id: str,
    resource_type: str,
) -> str:
    """
    Resolve a resource name or ID to an ID.

    Resolution order:
        1. Exact ID match - we can return the ID immediately
        2. Exact name match (case-sensitive)
        3. Case-insensitive name match

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
    # 1) Exact ID match
    id_matches = [r for r in resources if r.id == name_or_id]
    if len(id_matches) == 1:
        return id_matches[0].id

    # If it looks like a UUID but wasn't found, it's probably a wrong ID
    if is_uuid(name_or_id):
        raise ResourceNotFoundError(resource_type, name_or_id)

    # Exact name match (case-sensitive)
    name_matches = [r for r in resources if r.name == name_or_id]
    if len(name_matches) == 1:
        return name_matches[0].id
    if len(name_matches) > 1:
        raise AmbiguousResourceError(resource_type, name_or_id, name_matches)

    # Case-insensitive name match
    name_matches_ci = [r for r in resources if r.name.lower() == name_or_id.lower()]
    if len(name_matches_ci) == 1:
        return name_matches_ci[0].id
    if len(name_matches_ci) > 1:
        raise AmbiguousResourceError(resource_type, name_or_id, name_matches_ci)

    # No match found
    raise ResourceNotFoundError(resource_type, name_or_id)


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
    # This should never happen if resolve_resource_id worked correctly
    raise ResourceNotFoundError(resource_type, name_or_id)
