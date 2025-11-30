from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from exls.shared.adapters.gateway.file.gateways import (
    IFileReadGateway,
    IFileWriteGateway,
)
from exls.shared.adapters.ui.flows.keys import PublicKeySpecDTO
from exls.shared.core.service import ServiceError


class CryptoService:
    def __init__(
        self,
        file_reader: IFileReadGateway[str],
        file_writer: IFileWriteGateway[str],
    ):
        self._file_reader = file_reader
        self._file_writer = file_writer

    def resolve_public_key(self, spec: PublicKeySpecDTO) -> str:
        """
        Takes the user's intent (Spec) and returns the actual Public Key string.
        """
        if spec.create_new:
            return self._generate_and_save_key(
                spec.key_name if spec.key_name else "exls_key", spec.path
            )

        return self._load_key_from_file(spec.path)

    def _load_key_from_file(self, path: Path) -> str:
        try:
            return self._file_reader.read_file(path).strip()
        except Exception as e:
            raise ServiceError(f"Failed to load public key from {path}: {e}")

    def _generate_and_save_key(self, name: str, path: Path) -> str:
        """
        Generates an RSA key pair, saves it to the given path, and returns the public key content.
        """
        # path is the directory, name is the filename base
        file_path: Path = path / f"{name}.key"
        if file_path.exists():
            raise ServiceError(f"Key file already exists at {file_path}")

        # Ensure directory exists
        path.mkdir(parents=True, exist_ok=True)

        try:
            # Generate private key (RSA 4096)
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )

            # Serialize private key to OpenSSH/PEM format
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
                encryption_algorithm=serialization.NoEncryption(),
            )

            # Serialize public key to OpenSSH format
            public_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            )

            # Add comment to public key to match ssh-keygen behavior
            public_key_content = f"{public_bytes.decode('utf-8')} {name}\n"

            # Write private key
            self._file_writer.write_file(file_path, private_bytes.decode("utf-8"))
            # Set permissions to 600 (rw-------)
            file_path.chmod(0o600)

            # Write public key (replace .key extension with .pub)
            public_key_path = file_path.with_suffix(".pub")
            self._file_writer.write_file(public_key_path, public_key_content)

            return public_key_content

        except Exception as e:
            raise ServiceError(f"Failed to generate SSH key: {e}")
