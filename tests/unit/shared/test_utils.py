import sys
from unittest.mock import MagicMock, patch

# Mock coolname before importing the module under test
sys.modules["coolname"] = MagicMock()

import pytest  # noqa: E402

from exls.shared.core.utils import (  # noqa: E402
    deep_merge,
    generate_random_name,
    validate_kubernetes_name,
)


class TestGenerateRandomName:
    @patch("exls.shared.core.utils.generate_slug")
    def test_generate_random_name_defaults(self, mock_generate_slug: MagicMock) -> None:
        """Test generating random name with default arguments."""
        # Arrange
        mock_generate_slug.return_value = "generated-slug"

        # Act
        result = generate_random_name()

        # Assert
        assert result == "exls-generated-slug"
        mock_generate_slug.assert_called_once_with(2)

    @patch("exls.shared.core.utils.generate_slug")
    def test_generate_random_name_custom(self, mock_generate_slug: MagicMock) -> None:
        """Test generating random name with custom arguments."""
        # Arrange
        prefix = "custom"
        slug_length = 4
        mock_generate_slug.return_value = "long-generated-slug"

        # Act
        result = generate_random_name(prefix=prefix, slug_length=slug_length)

        # Assert
        assert result == "custom-long-generated-slug"
        mock_generate_slug.assert_called_once_with(slug_length)


class TestValidateKubernetesName:
    def test_validate_kubernetes_name_valid(self) -> None:
        """Test valid kubernetes names."""
        valid_names = ["my-service", "app-1", "frontend-api-v2", "z", "0-0", "a" * 63]
        for name in valid_names:
            assert validate_kubernetes_name(name) == name

    def test_validate_kubernetes_name_too_long(self) -> None:
        """Test name longer than 63 characters."""
        long_name = "a" * 64
        with pytest.raises(ValueError, match="Name must be 63 characters or less"):
            validate_kubernetes_name(long_name)

    def test_validate_kubernetes_name_invalid_chars(self) -> None:
        """Test names with invalid characters."""
        invalid_names = [
            "MyService",  # Uppercase
            "my_service",  # Underscore
            "my.service",  # Dot
            "my service",  # Space
            "-start",  # Starts with hyphen
            "end-",  # Ends with hyphen
        ]
        for name in invalid_names:
            with pytest.raises(
                ValueError, match="Name must consist of lower case alphanumeric"
            ):
                validate_kubernetes_name(name)

    def test_validate_kubernetes_name_edge_cases(self) -> None:
        """Test edge cases for validation."""
        # Empty string should fail
        with pytest.raises(ValueError):
            validate_kubernetes_name("")

        # Consecutive hyphens are valid in DNS-1123
        assert validate_kubernetes_name("my--app") == "my--app"

        # Numeric only is valid
        assert validate_kubernetes_name("123") == "123"


class TestDeepMerge:
    def test_deep_merge_simple(self) -> None:
        """Test simple merge of two dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        expected = {"a": 1, "b": 3, "c": 4}
        assert deep_merge(dict1, dict2) == expected

    def test_deep_merge_nested(self) -> None:
        """Test recursive merge of nested dictionaries."""
        dict1 = {"a": {"x": 1, "y": 2}, "b": 5}
        dict2 = {"a": {"y": 3, "z": 4}, "c": 6}
        expected = {"a": {"x": 1, "y": 3, "z": 4}, "b": 5, "c": 6}
        assert deep_merge(dict1, dict2) == expected

    def test_deep_merge_multiple(self) -> None:
        """Test merging more than two dictionaries."""
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        dict3 = {"c": 3}
        expected = {"a": 1, "b": 2, "c": 3}
        assert deep_merge(dict1, dict2, dict3) == expected

    def test_deep_merge_type_mismatch(self) -> None:
        """Test overriding a dictionary with a primitive value and vice versa."""
        dict1 = {"a": {"x": 1}}
        dict2 = {"a": 2}
        assert deep_merge(dict1, dict2) == {"a": 2}

        dict3 = {"a": 2}
        dict4 = {"a": {"x": 1}}
        assert deep_merge(dict3, dict4) == {"a": {"x": 1}}

    def test_deep_merge_empty(self) -> None:
        """Test merging with empty dictionaries."""
        dict1 = {"a": 1}
        assert deep_merge(dict1, {}) == {"a": 1}
        assert deep_merge({}, dict1) == {"a": 1}
        assert deep_merge({}, {}) == {}

    def test_deep_merge_lists(self) -> None:
        """Test that lists are overwritten, not merged."""
        dict1 = {"items": [1, 2]}
        dict2 = {"items": [3, 4]}
        # Expect overwrite, not [1, 2, 3, 4]
        assert deep_merge(dict1, dict2) == {"items": [3, 4]}

    def test_deep_merge_none_override(self) -> None:
        """Test that None can override a value."""
        dict1 = {"a": 1}
        dict2 = {"a": None}
        assert deep_merge(dict1, dict2) == {"a": None}

    def test_deep_merge_reference_behavior(self) -> None:
        """
        Verify reference behavior.
        Current implementation is NOT a deep copy for non-merged values.
        This test documents that behavior.
        """
        nested_list = [1, 2]
        dict1 = {"a": nested_list}
        dict2 = {"b": 3}

        result = deep_merge(dict1, dict2)

        # The list in result is the SAME object as in dict1
        assert result["a"] is nested_list

        # Modifying the result affects the input
        result["a"].append(3)
        assert dict1["a"] == [1, 2, 3]
