from pathlib import Path
from typing import Any

import yaml

from exalsius.core.base.commands import BaseCommand, CommandError


class FileIOCommandError(CommandError):
    def __init__(self, message: str, file_path: str, retryable: bool = False):
        super().__init__(message)
        self.message: str = message
        self.file_path: str = file_path
        self.retryable: bool = retryable

    def __str__(self):
        return f"FileIO Error for {self.file_path}: {self.message}"


class WriteYamlFileCommand(BaseCommand[None]):
    def __init__(self, file_path: Path, content: str):
        self._file_path: Path = file_path
        self._content: str = content

    def execute(self) -> None:
        try:
            yaml_dict: dict[str, Any] = yaml.safe_load(self._content)
            yaml_pretty: str = yaml.dump(
                yaml_dict, sort_keys=False, default_flow_style=False
            )
            file_dir: Path = Path(self._file_path).parent
            file_dir.mkdir(parents=True, exist_ok=True)
            with open(self._file_path, "w") as file:
                file.write(yaml_pretty)
        except FileNotFoundError as e:
            raise FileIOCommandError(
                message=f"File not found: {self._file_path}",
                file_path=str(self._file_path),
                retryable=False,
            ) from e
        except PermissionError as e:
            raise FileIOCommandError(
                message=f"Permission denied: {self._file_path}",
                file_path=str(self._file_path),
                retryable=False,
            ) from e
        except yaml.YAMLError as e:
            raise FileIOCommandError(
                message=f"Failed to parse YAML file: {e}",
                file_path=str(self._file_path),
                retryable=False,
            ) from e
        except OSError as e:
            raise FileIOCommandError(
                message=f"Failed to write YAML file: {e}",
                file_path=str(self._file_path),
                retryable=True,
            ) from e
        except Exception as e:
            raise FileIOCommandError(
                message=f"Unexpected error while writing YAML file: {e}",
                file_path=str(self._file_path),
                retryable=True,
            ) from e


class ReadYamlFileCommand(BaseCommand[dict[str, Any]]):
    def __init__(self, file_path: Path):
        self._file_path: Path = file_path

    def execute(self) -> dict[str, Any]:
        try:
            with open(self._file_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileIOCommandError(
                message=f"File not found: {self._file_path}",
                file_path=str(self._file_path),
                retryable=False,
            ) from e
        except PermissionError as e:
            raise FileIOCommandError(
                message=f"Permission denied: {self._file_path}",
                file_path=str(self._file_path),
                retryable=False,
            ) from e
        except yaml.YAMLError as e:
            raise FileIOCommandError(
                message=f"Failed to parse YAML file: {e}",
                file_path=str(self._file_path),
                retryable=False,
            ) from e
        except OSError as e:
            raise FileIOCommandError(
                message=f"Failed to read YAML file: {e}",
                file_path=str(self._file_path),
                retryable=True,
            ) from e
        except Exception as e:
            raise FileIOCommandError(
                message=f"Unexpected error while reading YAML file: {e}",
                file_path=str(self._file_path),
                retryable=True,
            ) from e
