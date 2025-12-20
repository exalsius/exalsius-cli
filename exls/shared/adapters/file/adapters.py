import base64
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, TypeVar, Union, cast

import yaml

from exls.shared.adapters.file.commands import (
    ReadBinaryFileCommand,
    ReadStringFileCommand,
    ReadYamlFileCommand,
    WriteStringFileCommand,
    WriteYamlFileCommand,
)
from exls.shared.core.ports.command import CommandError
from exls.shared.core.ports.file import FileReadPort, FileWritePort

F = TypeVar("F", bound=Callable[..., Any])


def _resolve_path(func: F) -> F:
    @wraps(func)
    def wrapper(
        self: Any, file_path: Union[Path, str], *args: Any, **kwargs: Any
    ) -> Any:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        resolved_path = file_path.expanduser()
        return func(self, resolved_path, *args, **kwargs)

    return cast(F, wrapper)


class StringBase64FileReadAdapter(FileReadPort[str]):
    @_resolve_path
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


class YamlFileWriteAdapter(FileWritePort[str]):
    @_resolve_path
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


class YamlFileIOAdapter(FileReadPort[Dict[str, Any]], FileWritePort[Dict[str, Any]]):
    @_resolve_path
    def read_file(self, file_path: Path) -> Dict[str, Any]:
        command: ReadYamlFileCommand = ReadYamlFileCommand(file_path=file_path)
        return command.execute()

    @_resolve_path
    def write_file(self, file_path: Path, content: Dict[str, Any]) -> None:
        command: WriteYamlFileCommand = WriteYamlFileCommand(
            file_path=file_path, content=content
        )
        command.execute()


class StringFileIOAdapter(FileReadPort[str], FileWritePort[str]):
    @_resolve_path
    def read_file(self, file_path: Path) -> str:
        command: ReadStringFileCommand = ReadStringFileCommand(file_path=file_path)
        return command.execute()

    @_resolve_path
    def write_file(self, file_path: Path, content: str) -> None:
        command: WriteStringFileCommand = WriteStringFileCommand(
            file_path=file_path, content=content
        )
        command.execute()
