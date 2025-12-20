from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

T_FileContent = TypeVar("T_FileContent")


class FileReadPort(Generic[T_FileContent], ABC):
    @abstractmethod
    def read_file(self, file_path: Path) -> T_FileContent: ...


class FileWritePort(Generic[T_FileContent], ABC):
    @abstractmethod
    def write_file(self, file_path: Path, content: T_FileContent) -> None: ...
