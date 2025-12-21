from __future__ import annotations

from typing import List, cast

from pydantic import BaseModel, Field, StrictStr

from exls.clusters.core.domain import ClusterNode, ClusterType
from exls.clusters.core.service import ClustersService
from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.flow.flow import (
    FlowCancelationByUserException,
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
from exls.shared.adapters.ui.input.service import kubernetes_name_validator
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.core.utils import generate_random_name


class FlowClusterNodeDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster node")
    name: StrictStr = Field(..., description="The name of the cluster node")


class FlowDeployClusterRequestDTO(BaseModel):
    name: StrictStr = Field(default="", description="The name of the cluster")
    cluster_type: ClusterType = Field(
        default=ClusterType.REMOTE, description="The type of the cluster"
    )
    worker_node_ids: List[FlowClusterNodeDTO] = Field(
        default_factory=lambda: cast(List[FlowClusterNodeDTO], []),
        description="The worker nodes",
    )
    control_plane_node_ids: List[FlowClusterNodeDTO] = Field(
        default_factory=lambda: cast(List[FlowClusterNodeDTO], []),
        description="The control plane nodes",
    )
    enable_multinode_training: bool = Field(
        default=False,
        description="Enable multinode AI model training for the cluster",
    )
    enable_telemetry: bool = Field(
        default=False, description="Enable telemetry for the cluster"
    )
    enable_vpn: bool = Field(default=False, description="Enable VPN for the cluster")


class DeployClusterFlow(FlowStep[FlowDeployClusterRequestDTO]):
    def __init__(self, service: ClustersService):
        self._service: ClustersService = service

    def _get_worker_node_choices(
        self, model: FlowDeployClusterRequestDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterNodeDTO]:
        deployable_nodes: List[ClusterNode] = self._service.list_available_nodes()
        if len(deployable_nodes) == 0:
            raise InvalidFlowStateError(
                "No deployable nodes in your node pool found. You need to import nodes first and they need to be in status 'AVAILABLE'."
            )
        return ChoicesSpec[FlowClusterNodeDTO](
            choices=[
                DisplayChoice[FlowClusterNodeDTO](
                    title=node.hostname,
                    value=FlowClusterNodeDTO(id=node.id, name=node.hostname),
                )
                for node in deployable_nodes
            ],
        )

    def _run(
        self,
        model: FlowDeployClusterRequestDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow: SequentialFlow[FlowDeployClusterRequestDTO] = SequentialFlow[
            FlowDeployClusterRequestDTO
        ](
            steps=[
                TextInputStep[FlowDeployClusterRequestDTO](
                    key="name",
                    message="Name:",
                    default=generate_random_name(prefix="exls-cluster"),
                    validator=kubernetes_name_validator,
                ),
                CheckboxStep[FlowDeployClusterRequestDTO, FlowClusterNodeDTO](
                    key="worker_node_ids",
                    message="Select worker nodes:",
                    choices_spec=self._get_worker_node_choices,
                ),
                ConfirmStep[FlowDeployClusterRequestDTO](
                    key="enable_multinode_training",
                    message="Enable multinode AI model training for the cluster?",
                    default=False,
                ),
                ConfirmStep[FlowDeployClusterRequestDTO](
                    key="enable_vpn",
                    message="Enable VPN for the cluster?",
                    default=False,
                ),
                # ConfirmStep[DeployClusterRequestFromFlowDTO](
                #     key="enable_telemetry",
                #     message="Enable telemetry for the cluster?",
                #     default=False,
                # ),
            ]
        )
        flow.execute(model, context, io_facade)

    def _confirm_import(
        self,
        deploy_cluster_request: FlowDeployClusterRequestDTO,
        io_facade: IOFacade[BaseModel],
    ) -> bool:
        io_facade.display_info_message(
            message="Deploying the following cluster:", output_format=OutputFormat.TEXT
        )
        io_facade.display_data(
            data=deploy_cluster_request, output_format=OutputFormat.TABLE
        )
        confirmed: bool = io_facade.ask_confirm(
            message="Deploy this cluster?", default=True
        )
        return confirmed

    def execute(
        self,
        model: FlowDeployClusterRequestDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        deployable_nodes: List[ClusterNode] = self._service.list_available_nodes()
        if len(deployable_nodes) == 0:
            raise InvalidFlowStateError(
                "No deployable nodes in your node pool found. You need to import nodes first and they need to be in status 'AVAILABLE'."
            )
        io_facade.display_info_message(
            message="🚀 Deploying a new cluster - Interactive Mode: This will guide you through the process of deploying a new cluster",
            output_format=OutputFormat.TEXT,
        )

        self._run(model, context, io_facade)

        if not self._confirm_import(model, io_facade):
            raise FlowCancelationByUserException(
                "Cluster deployment cancelled by user."
            )
