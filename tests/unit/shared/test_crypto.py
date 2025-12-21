from pathlib import Path
from unittest.mock import ANY, MagicMock, Mock, patch

import pytest
from cryptography.hazmat.primitives import serialization

from exls.shared.adapters.ui.flows.keys import PublicKeySpecDTO
from exls.shared.core.crypto import CryptoService
from exls.shared.core.exceptions import ServiceError
from exls.shared.core.ports.file import FileReadPort, FileWritePort


@pytest.fixture
def mock_file_reader() -> Mock:
    return Mock(spec=FileReadPort)


@pytest.fixture
def mock_file_writer() -> Mock:
    return Mock(spec=FileWritePort)


@pytest.fixture
def crypto_service(mock_file_reader: Mock, mock_file_writer: Mock) -> CryptoService:
    return CryptoService(mock_file_reader, mock_file_writer)


class TestCryptoService:
    def test_resolve_public_key_existing_success(
        self, crypto_service: CryptoService, mock_file_reader: Mock
    ) -> None:
        # Arrange
        path = Path("/path/to/key.pub")
        spec = PublicKeySpecDTO(create_new=False, path=path)
        expected_key = "ssh-rsa AAAAB3Nza... test-key"

        mock_file_reader.read_file.return_value = expected_key

        # Act
        result = crypto_service.resolve_public_key(spec)

        # Assert
        assert result == expected_key
        mock_file_reader.read_file.assert_called_once_with(path)

    def test_resolve_public_key_existing_strips_whitespace(
        self, crypto_service: CryptoService, mock_file_reader: Mock
    ) -> None:
        # Arrange
        path = Path("/path/to/key.pub")
        spec = PublicKeySpecDTO(create_new=False, path=path)
        dirty_key = "\n  ssh-rsa AAAAB3...  \n"
        clean_key = "ssh-rsa AAAAB3..."

        mock_file_reader.read_file.return_value = dirty_key

        # Act
        result = crypto_service.resolve_public_key(spec)

        # Assert
        assert result == clean_key

    def test_resolve_public_key_existing_failure(
        self, crypto_service: CryptoService, mock_file_reader: Mock
    ) -> None:
        # Arrange
        path = Path("/nonexistent/key.pub")
        spec = PublicKeySpecDTO(create_new=False, path=path)

        mock_file_reader.read_file.side_effect = Exception("File not found")

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            crypto_service.resolve_public_key(spec)

        assert f"Failed to load public key from {path}" in str(exc_info.value)

    @patch("exls.shared.core.crypto.rsa.generate_private_key")
    def test_resolve_public_key_generate_new_success(
        self, mock_rsa_gen: Mock, crypto_service: CryptoService, mock_file_writer: Mock
    ) -> None:
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_key_path = MagicMock(spec=Path)
        mock_pub_key_path = MagicMock(spec=Path)

        # Setup path arithmetic: path / "exls_key.key"
        mock_path.__truediv__.return_value = mock_key_path

        # Setup key file checks
        mock_key_path.exists.return_value = False
        mock_key_path.with_suffix.return_value = mock_pub_key_path

        # Setup Mock RSA Key
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_rsa_gen.return_value = mock_private_key
        mock_private_key.public_key.return_value = mock_public_key

        mock_private_key.private_bytes.return_value = b"private_bytes"
        mock_public_key.public_bytes.return_value = b"public_bytes"

        spec = PublicKeySpecDTO(create_new=True, path=mock_path, key_name="exls_key")

        # Act
        result = crypto_service.resolve_public_key(spec)

        # Assert
        # 1. Check directory creation
        mock_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # 2. Check RSA key generation params
        mock_rsa_gen.assert_called_once_with(public_exponent=65537, key_size=4096)

        # 3. Check serialization calls
        mock_private_key.private_bytes.assert_called_once_with(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=ANY,  # We can check instance of NoEncryption if needed
        )
        mock_public_key.public_bytes.assert_called_once_with(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )

        # 4. Check file writing
        assert mock_file_writer.write_file.call_count == 2

        # Check private key write
        mock_file_writer.write_file.assert_any_call(mock_key_path, "private_bytes")
        # Check permissions
        mock_key_path.chmod.assert_called_once_with(0o600)

        # Check public key write
        expected_pub_content = "public_bytes exls_key\n"
        mock_file_writer.write_file.assert_any_call(
            mock_pub_key_path, expected_pub_content
        )

        assert result == expected_pub_content

    @patch("exls.shared.core.crypto.rsa.generate_private_key")
    def test_resolve_public_key_generate_defaults_name(
        self, mock_rsa_gen: Mock, crypto_service: CryptoService, mock_file_writer: Mock
    ) -> None:
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_key_path = MagicMock(spec=Path)
        mock_pub_key_path = MagicMock(spec=Path)

        # We need to ensure the path operations don't fail
        # crypto.py line 42: file_path: Path = path / f"{name}.key"
        # crypto.py line 43: if file_path.exists():

        mock_path.__truediv__.return_value = mock_key_path
        mock_key_path.exists.return_value = False
        mock_key_path.with_suffix.return_value = mock_pub_key_path

        # Mock RSA gen to avoid actual generation
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_rsa_gen.return_value = mock_private_key
        mock_private_key.public_key.return_value = mock_public_key
        mock_private_key.private_bytes.return_value = b"priv"
        mock_public_key.public_bytes.return_value = b"pub"

        spec = PublicKeySpecDTO(create_new=True, path=mock_path, key_name=None)

        # Act
        crypto_service.resolve_public_key(spec)

        # Assert
        # The key name logic happens before file path construction:
        # file_path: Path = path / f"{name}.key"
        # So we verify that path / "exls_key.key" was called.
        mock_path.__truediv__.assert_called_with("exls_key.key")

    def test_resolve_public_key_generate_file_exists(
        self, crypto_service: CryptoService
    ) -> None:
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_key_path = MagicMock(spec=Path)

        mock_path.__truediv__.return_value = mock_key_path
        mock_key_path.exists.return_value = True  # File already exists

        spec = PublicKeySpecDTO(create_new=True, path=mock_path, key_name="test_key")

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            crypto_service.resolve_public_key(spec)

        assert "Key file already exists" in str(exc_info.value)

    @patch("exls.shared.core.crypto.rsa.generate_private_key")
    def test_resolve_public_key_generation_failure(
        self, mock_rsa_gen: Mock, crypto_service: CryptoService
    ) -> None:
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_key_path = MagicMock(spec=Path)

        mock_path.__truediv__.return_value = mock_key_path
        mock_key_path.exists.return_value = False

        # Simulate error during key generation
        mock_rsa_gen.side_effect = Exception("RSA Error")

        spec = PublicKeySpecDTO(create_new=True, path=mock_path, key_name="test_key")

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            crypto_service.resolve_public_key(spec)

        assert "Failed to generate SSH key: RSA Error" in str(exc_info.value)

    @patch("exls.shared.core.crypto.rsa.generate_private_key")
    def test_resolve_public_key_generate_chmod_failure(
        self, mock_rsa_gen: Mock, crypto_service: CryptoService, mock_file_writer: Mock
    ) -> None:
        # Arrange
        mock_path = MagicMock(spec=Path)
        mock_key_path = MagicMock(spec=Path)
        mock_pub_key_path = MagicMock(spec=Path)

        mock_path.__truediv__.return_value = mock_key_path
        mock_key_path.exists.return_value = False
        mock_key_path.with_suffix.return_value = mock_pub_key_path

        # Simulate chmod failure
        mock_key_path.chmod.side_effect = OSError("Permission denied")

        # Mock keys
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_rsa_gen.return_value = mock_private_key
        mock_private_key.public_key.return_value = mock_public_key
        mock_private_key.private_bytes.return_value = b"priv"
        mock_public_key.public_bytes.return_value = b"pub"

        spec = PublicKeySpecDTO(create_new=True, path=mock_path, key_name="test")

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            crypto_service.resolve_public_key(spec)

        assert "Failed to generate SSH key: Permission denied" in str(exc_info.value)
        # Verify private key was written before failure
        assert mock_file_writer.write_file.call_count == 1
