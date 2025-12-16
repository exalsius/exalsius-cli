from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field, StrictStr

from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, FlowStep


class FlowNodesSshKeySpecification(BaseModel):
    name: StrictStr = Field(default="", description="The name of the SSH key")
    key_path: Path = Field(default=Path(""), description="The path to the SSH key file")


class IImportSshKeyFlow(FlowStep[FlowNodesSshKeySpecification], ABC):
    @abstractmethod
    def execute(
        self,
        model: FlowNodesSshKeySpecification,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
    ) -> None: ...
