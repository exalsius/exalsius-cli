import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, TypeVar

import yaml

from exls.shared.adapters.gateway.file.commands import (
    ReadBinaryFileCommand,
    ReadStringFileCommand,
    ReadYamlFileCommand,
    WriteStringFileCommand,
    WriteYamlFileCommand,
)
from exls.shared.core.ports.command import CommandError

T_FileContent = TypeVar("T_FileContent")


class IFileReadGateway(Generic[T_FileContent], ABC):
    @abstractmethod
    def read_file(self, file_path: Path) -> T_FileContent: ...


class IFileWriteGateway(Generic[T_FileContent], ABC):
    @abstractmethod
    def write_file(self, file_path: Path, content: T_FileContent) -> None: ...


class StringBase64FileReadGateway(IFileReadGateway[str]):
    def read_file(self, file_path: Path) -> str:
        try:
            command: ReadBinaryFileCommand = ReadBinaryFileCommand(file_path=file_path)
            content: bytes = command.execute()
            content_base64: str = base64.b64encode(content).decode("utf-8")
        except Exception as e:
            raise CommandError(
                message=f"Failed to read file {file_path}: {str(e)}",
            )
        return content_base64


class YamlFileWriteGateway(IFileWriteGateway[str]):
    def write_file(self, file_path: Path, content: str) -> None:
        try:
            content_dict: Dict[str, Any] = yaml.safe_load(content)
            command: WriteYamlFileCommand = WriteYamlFileCommand(
                file_path=file_path, content=content_dict
            )
            command.execute()
        except yaml.YAMLError as e:
            raise CommandError(
                message=f"Failed to parse YAML string: {str(e)}",
            )
        except Exception as e:
            raise CommandError(
                message=f"Failed to write YAML file {file_path}: {str(e)}",
            )


class YamlFileIOGateway(
    IFileReadGateway[Dict[str, Any]], IFileWriteGateway[Dict[str, Any]]
):
    def read_file(self, file_path: Path) -> Dict[str, Any]:
        command: ReadYamlFileCommand = ReadYamlFileCommand(file_path=file_path)
        return command.execute()

    def write_file(self, file_path: Path, content: Dict[str, Any]) -> None:
        command: WriteYamlFileCommand = WriteYamlFileCommand(
            file_path=file_path, content=content
        )
        command.execute()


class StringFileIOGateway(IFileReadGateway[str], IFileWriteGateway[str]):
    def read_file(self, file_path: Path) -> str:
        command: ReadStringFileCommand = ReadStringFileCommand(file_path=file_path)
        return command.execute()

    def write_file(self, file_path: Path, content: str) -> None:
        command: WriteStringFileCommand = WriteStringFileCommand(
            file_path=file_path, content=content
        )
        command.execute()
