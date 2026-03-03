"""PKCE (RFC 7636) utility functions."""

import base64
import hashlib
import secrets


def generate_code_verifier(length: int = 64) -> str:
    """Generate cryptographically secure code verifier (43-128 chars, RFC 7636 §4.1)."""
    if length < 43 or length > 128:
        raise ValueError("Code verifier length must be between 43 and 128")
    return secrets.token_urlsafe(length)[:length]


def generate_code_challenge(verifier: str) -> str:
    """Generate S256 code challenge (RFC 7636 §4.2)."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def generate_state(length: int = 32) -> str:
    """Generate CSRF protection state parameter."""
    return secrets.token_urlsafe(length)


def generate_nonce(length: int = 32) -> str:
    """Generate nonce for replay attack prevention."""
    return secrets.token_urlsafe(length)
