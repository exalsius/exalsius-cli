import re


def non_empty_string_validator(text: str) -> bool | str:
    """Validator for non-empty strings."""
    return True if len(text.strip()) > 0 else "Please enter a valid string."


def min_length_validator(text: str, min_length: int) -> bool | str:
    """Validator for minimum length."""
    return (
        True
        if len(text.strip()) >= min_length
        else f"Please enter a string with at least {min_length} characters."
    )


def kubernetes_name_validator(text: str) -> bool | str:
    """Validator for Kubernetes names."""
    if len(text.strip()) > 63:
        return "Name must be 63 characters or less."
    if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", text):
        return "Name must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character."
    return True


def ipv4_address_validator(text: str) -> bool | str:
    """Validator for IPv4 addresses with an optional port."""
    if not text:
        return "The value cannot be empty."
    match = re.match(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::(\d{1,5}))?$",
        text,
    )
    if not match:
        return "Please enter a valid IPv4 address, with an optional port."

    if (port_str := match.group(1)) is not None:
        port = int(port_str)
        if not 0 <= port <= 65535:
            return f"Port number must be between 0 and 65535, but got {port}."

    return True


def positive_integer_validator(text: str) -> bool | str:
    """Validator for positive integers."""
    try:
        int(text)
    except ValueError:
        return "Please enter a valid integer."
    return True if int(text) > 0 else "Please enter a positive integer."
