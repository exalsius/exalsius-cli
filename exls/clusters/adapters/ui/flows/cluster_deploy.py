from typing import List

from pydantic import BaseModel

from exls.clusters.adapters.ui.dtos import (
    DeployClusterRequestFromFlowDTO,
    UnassignedClusterNodeDTO,
)
from exls.clusters.core.domain import UnassignedClusterNode
from exls.clusters.core.service import ClustersService
from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import (
    FlowContext,
    FlowStep,
    InvalidFlowStateError,
    SequentialFlow,
)
from exls.shared.adapters.ui.flow.steps import (
    CheckboxStep,
    ChoicesSpec,
    ConfirmStep,
    TextInputStep,
)
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.core.domain import generate_random_name


class DeployClusterFlow(FlowStep[DeployClusterRequestFromFlowDTO]):
    def __init__(self, service: ClustersService):
        self._service: ClustersService = service

    def _get_worker_node_choices(
        self, model: DeployClusterRequestFromFlowDTO, context: FlowContext
    ) -> ChoicesSpec[UnassignedClusterNodeDTO]:
        deployable_nodes: List[UnassignedClusterNode] = (
            self._service.get_deployable_nodes()
        )
        return ChoicesSpec[UnassignedClusterNodeDTO](
            choices=[
                DisplayChoice[UnassignedClusterNodeDTO](
                    title=node.hostname,
                    value=UnassignedClusterNodeDTO(id=node.id, name=node.hostname),
                )
                for node in deployable_nodes
            ],
        )

    def execute(
        self,
        model: DeployClusterRequestFromFlowDTO,
        context: FlowContext,
        io_facade: IIOFacade[BaseModel],
    ) -> None:
        deployable_nodes: List[UnassignedClusterNode] = (
            self._service.get_deployable_nodes()
        )
        # TODO: We can check and ask to initiate a node import flow if no deployable nodes are found
        if len(deployable_nodes) == 0:
            raise InvalidFlowStateError("No deployable nodes found")

        flow: SequentialFlow[DeployClusterRequestFromFlowDTO] = SequentialFlow[
            DeployClusterRequestFromFlowDTO
        ](
            steps=[
                TextInputStep[DeployClusterRequestFromFlowDTO](
                    key="name",
                    message="Name:",
                    default=generate_random_name(prefix="exls-cluster"),
                ),
                CheckboxStep[DeployClusterRequestFromFlowDTO, UnassignedClusterNodeDTO](
                    key="worker_node_ids",
                    message="Select worker nodes:",
                    choices_spec=self._get_worker_node_choices,
                ),
                ConfirmStep[DeployClusterRequestFromFlowDTO](
                    key="enable_multinode_training",
                    message="Enable multinode AI model training for the cluster?",
                    default=False,
                ),
                ConfirmStep[DeployClusterRequestFromFlowDTO](
                    key="enable_vpn",
                    message="Enable VPN for the cluster?",
                    default=False,
                ),
                ConfirmStep[DeployClusterRequestFromFlowDTO](
                    key="enable_telemetry",
                    message="Enable telemetry for the cluster?",
                    default=False,
                ),
            ]
        )
        flow.execute(model, context, io_facade)
