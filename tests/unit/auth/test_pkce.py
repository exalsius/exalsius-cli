"""Unit tests for PKCE utility functions."""

import pytest

from exls.auth.core.pkce import (
    generate_code_challenge,
    generate_code_verifier,
    generate_nonce,
    generate_state,
)


class TestGenerateCodeVerifier:
    def test_default_length(self):
        verifier = generate_code_verifier()
        assert len(verifier) == 64

    def test_custom_length(self):
        verifier = generate_code_verifier(length=43)
        assert len(verifier) == 43

    def test_max_length(self):
        verifier = generate_code_verifier(length=128)
        assert len(verifier) == 128

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="between 43 and 128"):
            generate_code_verifier(length=42)

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="between 43 and 128"):
            generate_code_verifier(length=129)

    def test_url_safe_characters(self):
        verifier = generate_code_verifier()
        # URL-safe base64 only contains alphanumeric, hyphen, underscore
        for char in verifier:
            assert char.isalnum() or char in ("-", "_")

    def test_uniqueness(self):
        v1 = generate_code_verifier()
        v2 = generate_code_verifier()
        assert v1 != v2


class TestGenerateCodeChallenge:
    def test_deterministic_for_same_verifier(self):
        verifier = "test-verifier-that-is-long-enough-for-testing-purposes-here"
        c1 = generate_code_challenge(verifier)
        c2 = generate_code_challenge(verifier)
        assert c1 == c2

    def test_different_for_different_verifiers(self):
        c1 = generate_code_challenge("verifier-a-long-enough-for-test-purposes-here-ok")
        c2 = generate_code_challenge("verifier-b-long-enough-for-test-purposes-here-ok")
        assert c1 != c2

    def test_no_padding(self):
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        assert "=" not in challenge

    def test_url_safe_characters(self):
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        for char in challenge:
            assert char.isalnum() or char in ("-", "_")


class TestGenerateState:
    def test_uniqueness(self):
        s1 = generate_state()
        s2 = generate_state()
        assert s1 != s2

    def test_non_empty(self):
        assert len(generate_state()) > 0


class TestGenerateNonce:
    def test_uniqueness(self):
        n1 = generate_nonce()
        n2 = generate_nonce()
        assert n1 != n2

    def test_non_empty(self):
        assert len(generate_nonce()) > 0
