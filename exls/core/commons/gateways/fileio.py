import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, TypeVar

from exls.core.commons.gateways.commands.fileio import (
    ReadBinaryFileCommand,
    ReadStringFileCommand,
    ReadYamlFileCommand,
    WriteStringFileCommand,
    WriteYamlFileCommand,
)

T_FileContent = TypeVar("T_FileContent")


class BaseFileIOGateway(ABC, Generic[T_FileContent]):
    @abstractmethod
    def read_file(self, file_path: Path) -> T_FileContent:
        raise NotImplementedError

    @abstractmethod
    def write_file(self, file_path: Path, content: T_FileContent) -> None:
        raise NotImplementedError


class YamlFileIOGateway(BaseFileIOGateway[Dict[str, Any]]):
    def read_file(self, file_path: Path) -> Dict[str, Any]:
        command: ReadYamlFileCommand = ReadYamlFileCommand(file_path=file_path)
        return command.execute()

    def write_file(self, file_path: Path, content: Dict[str, Any]) -> None:
        command: WriteYamlFileCommand = WriteYamlFileCommand(
            file_path=file_path, content=content
        )
        command.execute()


class StringFileIOGateway(BaseFileIOGateway[str]):
    def read_file(self, file_path: Path) -> str:
        command: ReadStringFileCommand = ReadStringFileCommand(file_path=file_path)
        return command.execute()

    def read_file_base64(self, file_path: Path) -> str:
        command: ReadBinaryFileCommand = ReadBinaryFileCommand(file_path=file_path)
        content: bytes = command.execute()
        return base64.b64encode(content).decode("utf-8")

    def write_file(self, file_path: Path, content: str) -> None:
        command: WriteStringFileCommand = WriteStringFileCommand(
            file_path=file_path, content=content
        )
        command.execute()
