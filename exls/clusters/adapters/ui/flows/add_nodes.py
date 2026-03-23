from __future__ import annotations

from typing import List, cast

from pydantic import BaseModel, Field

from exls.clusters.adapters.ui.flows.cluster_deploy import FlowClusterNodeDTO
from exls.clusters.core.domain import ClusterNode
from exls.clusters.core.service import ClustersService
from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.flow.flow import (
    FlowCancelationByUserException,
    FlowContext,
    FlowStep,
    InvalidFlowStateError,
    SequentialFlow,
)
from exls.shared.adapters.ui.flow.steps import CheckboxStep, ChoicesSpec
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.adapters.ui.output.values import OutputFormat


class FlowAddNodesRequestDTO(BaseModel):
    worker_node_ids: List[FlowClusterNodeDTO] = Field(
        default_factory=lambda: cast(List[FlowClusterNodeDTO], []),
        description="The worker nodes to add",
    )


class AddNodesFlow(FlowStep[FlowAddNodesRequestDTO]):
    def __init__(self, service: ClustersService, cluster_id: str):
        self._service: ClustersService = service
        self._cluster_id: str = cluster_id

    def _get_worker_node_choices(
        self, model: FlowAddNodesRequestDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterNodeDTO]:
        available_nodes: List[ClusterNode] = self._service.list_available_nodes()
        if len(available_nodes) == 0:
            raise InvalidFlowStateError(
                "No available nodes found in your node pool. You need to import nodes first and they need to be in status 'AVAILABLE'."
            )
        return ChoicesSpec[FlowClusterNodeDTO](
            choices=[
                DisplayChoice[FlowClusterNodeDTO](
                    title=node.hostname,
                    value=FlowClusterNodeDTO(id=node.id, name=node.hostname),
                )
                for node in available_nodes
            ],
        )

    def _run(
        self,
        model: FlowAddNodesRequestDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow: SequentialFlow[FlowAddNodesRequestDTO] = SequentialFlow[
            FlowAddNodesRequestDTO
        ](
            steps=[
                CheckboxStep[FlowAddNodesRequestDTO, FlowClusterNodeDTO](
                    key="worker_node_ids",
                    message="Select worker nodes to add:",
                    choices_spec=self._get_worker_node_choices,
                ),
            ]
        )
        flow.execute(model, context, io_facade)

    def _confirm(
        self,
        model: FlowAddNodesRequestDTO,
        io_facade: IOFacade[BaseModel],
    ) -> bool:
        node_names: str = ", ".join(n.name for n in model.worker_node_ids)
        io_facade.display_info_message(
            message=f"Adding the following worker nodes: {node_names}",
            output_format=OutputFormat.TEXT,
        )
        confirmed: bool = io_facade.ask_confirm(
            message="Add these nodes?", default=True
        )
        return confirmed

    def execute(
        self,
        model: FlowAddNodesRequestDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        available_nodes: List[ClusterNode] = self._service.list_available_nodes()
        if len(available_nodes) == 0:
            raise InvalidFlowStateError(
                "No available nodes found in your node pool. You need to import nodes first and they need to be in status 'AVAILABLE'."
            )
        io_facade.display_info_message(
            message="Adding nodes to cluster - Interactive Mode",
            output_format=OutputFormat.TEXT,
        )

        self._run(model, context, io_facade)

        if not self._confirm(model, io_facade):
            raise FlowCancelationByUserException("Add nodes cancelled by user.")
