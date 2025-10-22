from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from exalsius.core.commons.commands.fileio import (
    ReadYamlFileCommand,
    WriteYamlFileCommand,
)


class BaseFileIOGateway(ABC):
    @abstractmethod
    def read_file(self, file_path: Path) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def write_file(self, file_path: Path, content: str) -> None:
        raise NotImplementedError


class YamlFileIOGateway(BaseFileIOGateway):
    def read_file(self, file_path: Path) -> dict[str, Any]:
        command = ReadYamlFileCommand(file_path)
        return command.execute()

    def write_file(self, file_path: Path, content: str) -> None:
        command = WriteYamlFileCommand(file_path, content)
        command.execute()
