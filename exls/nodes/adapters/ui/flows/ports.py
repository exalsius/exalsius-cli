from abc import ABC, abstractmethod

from pydantic import BaseModel

from exls.nodes.adapters.ui.dtos import NodesSshKeySpecificationDTO
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, FlowStep


class IImportSshKeyFlow(FlowStep[NodesSshKeySpecificationDTO], ABC):
    @abstractmethod
    def execute(
        self,
        model: NodesSshKeySpecificationDTO,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
    ) -> None: ...
