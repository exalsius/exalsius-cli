from pathlib import Path
from typing import Any, Dict

import yaml

from exls.shared.core.ports.command import BaseCommand, CommandError


class FileIOCommandError(CommandError):
    def __init__(self, message: str, file_path: str, retryable: bool = False):
        super().__init__(message)
        self.message: str = message
        self.file_path: str = file_path
        self.retryable: bool = retryable

    def __str__(self):
        return f"FileIO Error for {self.file_path}: {self.message}"


class ReadStringFileCommand(BaseCommand[str]):
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def execute(self) -> str:
        with open(self._file_path, "r") as f:
            return f.read()


class WriteStringFileCommand(BaseCommand[None]):
    def __init__(self, file_path: Path, content: str):
        self._file_path = file_path
        self._content = content

    def execute(self) -> None:
        with open(self._file_path, "w") as f:
            f.write(self._content)


class ReadBinaryFileCommand(BaseCommand[bytes]):
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def execute(self) -> bytes:
        with open(self._file_path, "rb") as f:
            return f.read()


class WriteBinaryFileCommand(BaseCommand[None]):
    def __init__(self, file_path: Path, content: bytes):
        self._file_path = file_path
        self._content = content

    def execute(self) -> None:
        with open(self._file_path, "wb") as f:
            f.write(self._content)


class ReadYamlFileCommand(BaseCommand[Dict[str, Any]]):
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def execute(self) -> Dict[str, Any]:
        with open(self._file_path, "r") as f:
            return yaml.safe_load(f)


class WriteYamlFileCommand(BaseCommand[None]):
    def __init__(self, file_path: Path, content: Dict[str, Any]):
        self._file_path = file_path
        self._content = content

    def execute(self) -> None:
        with open(self._file_path, "w") as f:
            yaml.dump(self._content, f)
