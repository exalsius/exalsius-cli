import re
from typing import Any, Dict, cast

from coolname import generate_slug  # type: ignore


def generate_random_name(prefix: str = "exls", slug_length: int = 2) -> str:
    """Generate a random name."""
    return f"{prefix}-{generate_slug(slug_length)}"


def validate_kubernetes_name(name: str) -> str:
    """Validate that the name is a valid Kubernetes name."""
    if len(name) > 63:
        raise ValueError("Name must be 63 characters or less.")
    if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", name):
        raise ValueError(
            "Name must consist of lower case alphanumeric characters or '-', "
            "and must start and end with an alphanumeric character."
        )
    return name


def deep_merge(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Deep merges multiple dictionaries.
    Later dictionaries override earlier ones.
    Nested dictionaries are merged recursively.

    Args:
        *dicts: Variable number of dictionaries to merge.

    Returns:
        A new dictionary containing the merged result.
    """
    result: Dict[Any, Any] = {}
    for d in dicts:
        for k, v in d.items():
            if k in result and isinstance(result[k], Dict) and isinstance(v, Dict):
                result[k] = deep_merge(
                    cast(Dict[Any, Any], result[k]), cast(Dict[Any, Any], v)
                )
            else:
                result[k] = v
    return result
