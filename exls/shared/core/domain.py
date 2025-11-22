import re

from coolname import generate_slug  # type: ignore


class ExalsiusError(Exception):
    """Base exception for all Exalsius errors."""


class ExalsiusWarning(Warning):
    """Base warning for all Exalsius warnings."""


def generate_random_name(prefix: str = "exalsius", slug_length: int = 2) -> str:
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
