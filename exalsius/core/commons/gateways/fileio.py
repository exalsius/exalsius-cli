from abc import ABC, abstractmethod

from exalsius.core.commons.commands.fileio import WriteYamlFileCommand


class BaseFileIOGateway(ABC):
    @abstractmethod
    def read_file(self, file_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> None:
        raise NotImplementedError


class YamlFileIOGateway(BaseFileIOGateway):
    def read_file(self, file_path: str) -> str:
        raise NotImplementedError

    def write_file(self, file_path: str, content: str) -> None:
        command = WriteYamlFileCommand(file_path, content)
        command.execute()
