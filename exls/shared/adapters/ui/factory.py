from typing import Optional, Union

from pydantic import BaseModel

from exls.shared.adapters.ui.input.input import (
    ConsoleInputManager,
)
from exls.shared.adapters.ui.input.interfaces import (
    IInputManager,
)
from exls.shared.adapters.ui.output.interfaces import IOutputManager
from exls.shared.adapters.ui.output.output import TyperConsoleOutputManager
from exls.shared.adapters.ui.output.render.factory import (
    DefaultRendererProvider,
    RendererProvider,
)
from exls.shared.adapters.ui.output.render.table import Table


class IOFactory:
    def __init__(self, render_provider: Optional[RendererProvider[BaseModel]] = None):
        self._render_provider: RendererProvider[BaseModel] = (
            render_provider or DefaultRendererProvider[BaseModel]()
        )

    def get_output_manager(self) -> IOutputManager[BaseModel, Union[Table, str]]:
        return TyperConsoleOutputManager[BaseModel](
            object_renderer_provider=self._render_provider
        )

    def get_input_manager(self) -> IInputManager:
        return ConsoleInputManager()
