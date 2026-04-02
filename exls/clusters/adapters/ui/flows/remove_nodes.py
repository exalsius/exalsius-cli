from __future__ import annotations

from typing import List, cast

from pydantic import BaseModel, Field

from exls.clusters.adapters.ui.flows.cluster_deploy import FlowClusterNodeDTO
from exls.clusters.core.domain import Cluster, ClusterNode, ClusterNodeRole
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


class FlowRemoveNodesRequestDTO(BaseModel):
    nodes_to_remove: List[FlowClusterNodeDTO] = Field(
        default_factory=lambda: cast(List[FlowClusterNodeDTO], []),
        description="The nodes to remove",
    )


class RemoveNodesFlow(FlowStep[FlowRemoveNodesRequestDTO]):
    def __init__(self, service: ClustersService, cluster_id: str):
        self._service: ClustersService = service
        self._cluster_id: str = cluster_id

    def _get_worker_node_choices(
        self, model: FlowRemoveNodesRequestDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterNodeDTO]:
        cluster: Cluster = self._service.get_cluster(self._cluster_id)
        worker_nodes: List[ClusterNode] = [
            node for node in cluster.nodes if node.role == ClusterNodeRole.WORKER
        ]
        if len(worker_nodes) == 0:
            raise InvalidFlowStateError("No worker nodes found in this cluster.")
        return ChoicesSpec[FlowClusterNodeDTO](
            choices=[
                DisplayChoice[FlowClusterNodeDTO](
                    title=node.hostname,
                    value=FlowClusterNodeDTO(id=node.id, name=node.hostname),
                )
                for node in worker_nodes
            ],
        )

    def _run(
        self,
        model: FlowRemoveNodesRequestDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow: SequentialFlow[FlowRemoveNodesRequestDTO] = SequentialFlow[
            FlowRemoveNodesRequestDTO
        ](
            steps=[
                CheckboxStep[FlowRemoveNodesRequestDTO, FlowClusterNodeDTO](
                    key="nodes_to_remove",
                    message="Select worker nodes to remove:",
                    choices_spec=self._get_worker_node_choices,
                ),
            ]
        )
        flow.execute(model, context, io_facade)

    def _confirm(
        self,
        model: FlowRemoveNodesRequestDTO,
        io_facade: IOFacade[BaseModel],
    ) -> bool:
        node_names: str = ", ".join(n.name for n in model.nodes_to_remove)
        io_facade.display_info_message(
            message=f"Removing the following worker nodes: {node_names}",
            output_format=OutputFormat.TEXT,
        )
        confirmed: bool = io_facade.ask_confirm(
            message="Remove these nodes?", default=True
        )
        return confirmed

    def execute(
        self,
        model: FlowRemoveNodesRequestDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        cluster: Cluster = self._service.get_cluster(self._cluster_id)
        worker_nodes: List[ClusterNode] = [
            node for node in cluster.nodes if node.role == ClusterNodeRole.WORKER
        ]
        if len(worker_nodes) == 0:
            raise InvalidFlowStateError("No worker nodes found in this cluster.")
        io_facade.display_info_message(
            message="Removing nodes from cluster - Interactive Mode",
            output_format=OutputFormat.TEXT,
        )

        self._run(model, context, io_facade)

        if not self._confirm(model, io_facade):
            raise FlowCancelationByUserException("Remove nodes cancelled by user.")
