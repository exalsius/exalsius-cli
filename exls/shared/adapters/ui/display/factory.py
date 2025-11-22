from typing import Union

from pydantic import BaseModel

from exls.shared.adapters.ui.display.display import (
    QuestionaryInputManager,
    TyperConsoleOutputManager,
)
from exls.shared.adapters.ui.display.interfaces import (
    IBaseInputManager,
    IOutputManager,
)
from exls.shared.adapters.ui.display.render.factory import DefaultRendererProvider
from exls.shared.adapters.ui.display.render.table import Table


class InteractionManagerFactory:
    def get_output_manager(self) -> IOutputManager[BaseModel, Union[Table, str]]:
        render_provider = DefaultRendererProvider[BaseModel]()
        return TyperConsoleOutputManager[Union[Table, str]](
            object_renderer_provider=render_provider
        )

    def get_input_manager(self) -> IBaseInputManager:
        return QuestionaryInputManager()
