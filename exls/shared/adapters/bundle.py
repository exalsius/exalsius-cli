from abc import ABC, abstractmethod

import typer
from pydantic import BaseModel

from exls.config import AppConfig
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.utils import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    get_message_output_format_from_ctx,
    get_object_output_format_from_ctx,
)


class BaseBundle(ABC):
    def __init__(self, ctx: typer.Context):
        self._ctx: typer.Context = ctx

    @property
    def config(self) -> AppConfig:
        return get_config_from_ctx(self._ctx)

    @property
    def access_token(self) -> str:
        return get_access_token_from_ctx(self._ctx)

    @property
    def message_output_format(self) -> OutputFormat:
        return (
            get_message_output_format_from_ctx(self._ctx)
            or self.config.default_message_output_format
        )

    @property
    def object_output_format(self) -> OutputFormat:
        return (
            get_object_output_format_from_ctx(self._ctx)
            or self.config.default_object_output_format
        )

    @abstractmethod
    def get_io_facade(self) -> IIOFacade[BaseModel]: ...
