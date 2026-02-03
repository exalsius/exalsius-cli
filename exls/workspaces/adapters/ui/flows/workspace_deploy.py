"""Flows for interactive workspace deployment."""

from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.flow.flow import (
    FlowCancelationByUserException,
    FlowContext,
    FlowStep,
    SequentialFlow,
)
from exls.shared.adapters.ui.flow.steps import (
    ChoicesSpec,
    ConfirmStep,
    SelectRequiredStep,
    TextInputStep,
)
from exls.shared.adapters.ui.input.values import DisplayChoice
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.core.utils import generate_random_name
from exls.workspaces.adapters.ui.configurators import (
    DistributedTrainingModels,
    GradientCompression,
)
from exls.workspaces.adapters.ui.flows.access_flow import (
    AccessDTO,
    ConfigureWorkspaceAccessFlow,
)
from exls.workspaces.core.domain import WorkspaceCluster, WorkspaceClusterStatus
from exls.workspaces.core.service import WorkspacesService

# -----------------------------------------------------------------------------
# Shared Components
# -----------------------------------------------------------------------------


class FlowClusterDTO(BaseModel):
    """DTO for cluster selection in flows."""

    id: StrictStr = Field(..., description="The cluster ID")
    name: StrictStr = Field(..., description="The cluster name")


def _get_cluster_choices(
    service: WorkspacesService,
) -> ChoicesSpec[FlowClusterDTO]:
    """Get available clusters as choices for selection."""
    clusters: List[WorkspaceCluster] = service.list_clusters()
    ready_clusters = [c for c in clusters if c.status == WorkspaceClusterStatus.READY]
    return ChoicesSpec[FlowClusterDTO](
        choices=[
            DisplayChoice[FlowClusterDTO](
                title=f"{cluster.name}",
                value=FlowClusterDTO(id=cluster.id, name=cluster.name),
            )
            for cluster in ready_clusters
        ],
    )


def _min_length_validator(min_len: int, field_name: str):
    """Create a validator that checks minimum length."""

    def validator(value: str) -> bool | str:
        if len(value) >= min_len:
            return True
        return f"{field_name} must be at least {min_len} characters"

    return validator


def _positive_int_validator(value: str) -> bool | str:
    """Validate that value is a positive integer."""
    if value.isdigit() and int(value) >= 1:
        return True
    return "Must be a positive integer"


# -----------------------------------------------------------------------------
# Jupyter Flow
# -----------------------------------------------------------------------------


class DeployJupyterFlowDTO(BaseModel):
    """DTO for Jupyter workspace deployment flow."""

    cluster: Optional[FlowClusterDTO] = Field(
        default=None, description="The target cluster"
    )
    name: StrictStr = Field(default="", description="The workspace name")
    password: StrictStr = Field(default="", description="The Jupyter password")
    num_gpus: StrictStr = Field(default="1", description="Number of GPUs")
    wait_for_ready: bool = Field(
        default=False, description="Wait for workspace to be ready"
    )


class DeployJupyterFlow(FlowStep[DeployJupyterFlowDTO]):
    """Flow for collecting Jupyter workspace deployment inputs."""

    def __init__(self, service: WorkspacesService):
        self._service = service

    def _get_cluster_choices(
        self, model: DeployJupyterFlowDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterDTO]:
        return _get_cluster_choices(self._service)

    def execute(
        self,
        model: DeployJupyterFlowDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow: SequentialFlow[DeployJupyterFlowDTO] = SequentialFlow[
            DeployJupyterFlowDTO
        ](
            steps=[
                SelectRequiredStep[DeployJupyterFlowDTO, FlowClusterDTO](
                    key="cluster",
                    message="Select cluster:",
                    choices_spec=self._get_cluster_choices,
                ),
                TextInputStep[DeployJupyterFlowDTO](
                    key="name",
                    message="Workspace name:",
                    default=generate_random_name(prefix="jupyter"),
                ),
                TextInputStep[DeployJupyterFlowDTO](
                    key="password",
                    message="Jupyter password (min. 6 characters):",
                    validator=_min_length_validator(6, "Password"),
                ),
                TextInputStep[DeployJupyterFlowDTO](
                    key="num_gpus",
                    message="Number of GPUs:",
                    default="1",
                    validator=_positive_int_validator,
                ),
                ConfirmStep[DeployJupyterFlowDTO](
                    key="wait_for_ready",
                    message="Wait for workspace to be ready?",
                    default=False,
                ),
            ]
        )
        flow.execute(model, context, io_facade)

        # Confirmation
        io_facade.display_info_message(
            message="Deploying Jupyter workspace with the following configuration:",
            output_format=OutputFormat.TEXT,
        )
        io_facade.display_data(data=model, output_format=OutputFormat.TABLE)
        if not io_facade.ask_confirm(message="Deploy this workspace?", default=True):
            raise FlowCancelationByUserException("Deployment cancelled by user")


# -----------------------------------------------------------------------------
# Marimo Flow
# -----------------------------------------------------------------------------


class DeployMarimoFlowDTO(BaseModel):
    """DTO for Marimo workspace deployment flow."""

    cluster: Optional[FlowClusterDTO] = Field(
        default=None, description="The target cluster"
    )
    name: StrictStr = Field(default="", description="The workspace name")
    password: StrictStr = Field(
        default="", description="The Marimo password (optional)"
    )
    num_gpus: StrictStr = Field(default="1", description="Number of GPUs")
    wait_for_ready: bool = Field(
        default=False, description="Wait for workspace to be ready"
    )


class DeployMarimoFlow(FlowStep[DeployMarimoFlowDTO]):
    """Flow for collecting Marimo workspace deployment inputs."""

    def __init__(self, service: WorkspacesService):
        self._service = service

    def _get_cluster_choices(
        self, model: DeployMarimoFlowDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterDTO]:
        return _get_cluster_choices(self._service)

    def _validate_optional_password(self, value: str) -> bool | str:
        if value == "" or len(value) >= 6:
            return True
        return "Password must be at least 6 characters if provided"

    def execute(
        self,
        model: DeployMarimoFlowDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow: SequentialFlow[DeployMarimoFlowDTO] = SequentialFlow[DeployMarimoFlowDTO](
            steps=[
                SelectRequiredStep[DeployMarimoFlowDTO, FlowClusterDTO](
                    key="cluster",
                    message="Select cluster:",
                    choices_spec=self._get_cluster_choices,
                ),
                TextInputStep[DeployMarimoFlowDTO](
                    key="name",
                    message="Workspace name:",
                    default=generate_random_name(prefix="marimo"),
                ),
                TextInputStep[DeployMarimoFlowDTO](
                    key="password",
                    message="Marimo password (optional, min. 6 characters if set):",
                    default="",
                    validator=self._validate_optional_password,
                ),
                TextInputStep[DeployMarimoFlowDTO](
                    key="num_gpus",
                    message="Number of GPUs:",
                    default="1",
                    validator=_positive_int_validator,
                ),
                ConfirmStep[DeployMarimoFlowDTO](
                    key="wait_for_ready",
                    message="Wait for workspace to be ready?",
                    default=False,
                ),
            ]
        )
        flow.execute(model, context, io_facade)

        # Confirmation
        io_facade.display_info_message(
            message="Deploying Marimo workspace with the following configuration:",
            output_format=OutputFormat.TEXT,
        )
        io_facade.display_data(data=model, output_format=OutputFormat.TABLE)
        if not io_facade.ask_confirm(message="Deploy this workspace?", default=True):
            raise FlowCancelationByUserException("Deployment cancelled by user")


# -----------------------------------------------------------------------------
# DevPod Flow
# -----------------------------------------------------------------------------


class DeployDevPodFlowDTO(BaseModel):
    """DTO for DevPod workspace deployment flow."""

    cluster: Optional[FlowClusterDTO] = Field(
        default=None, description="The target cluster"
    )
    name: StrictStr = Field(default="", description="The workspace name")
    num_gpus: StrictStr = Field(default="1", description="Number of GPUs")
    access: AccessDTO = Field(
        default_factory=AccessDTO, description="SSH access configuration"
    )
    wait_for_ready: bool = Field(
        default=False, description="Wait for workspace to be ready"
    )


class DeployDevPodFlow(FlowStep[DeployDevPodFlowDTO]):
    """Flow for collecting DevPod workspace deployment inputs."""

    def __init__(
        self, service: WorkspacesService, access_flow: ConfigureWorkspaceAccessFlow
    ):
        self._service = service
        self._access_flow = access_flow

    def _get_cluster_choices(
        self, model: DeployDevPodFlowDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterDTO]:
        return _get_cluster_choices(self._service)

    def execute(
        self,
        model: DeployDevPodFlowDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        # Basic info flow
        basic_flow: SequentialFlow[DeployDevPodFlowDTO] = SequentialFlow[
            DeployDevPodFlowDTO
        ](
            steps=[
                SelectRequiredStep[DeployDevPodFlowDTO, FlowClusterDTO](
                    key="cluster",
                    message="Select cluster:",
                    choices_spec=self._get_cluster_choices,
                ),
                TextInputStep[DeployDevPodFlowDTO](
                    key="name",
                    message="Workspace name:",
                    default=generate_random_name(prefix="dev-pod"),
                ),
                TextInputStep[DeployDevPodFlowDTO](
                    key="num_gpus",
                    message="Number of GPUs:",
                    default="1",
                    validator=_positive_int_validator,
                ),
            ]
        )
        basic_flow.execute(model, context, io_facade)

        # Access configuration (uses nested flow)
        self._access_flow.execute(model.access, context, io_facade)

        # Wait for ready
        wait_flow: SequentialFlow[DeployDevPodFlowDTO] = SequentialFlow[
            DeployDevPodFlowDTO
        ](
            steps=[
                ConfirmStep[DeployDevPodFlowDTO](
                    key="wait_for_ready",
                    message="Wait for workspace to be ready?",
                    default=False,
                ),
            ]
        )
        wait_flow.execute(model, context, io_facade)

        # Confirmation
        io_facade.display_info_message(
            message="Deploying DevPod workspace with the following configuration:",
            output_format=OutputFormat.TEXT,
        )
        io_facade.display_data(data=model, output_format=OutputFormat.TABLE)
        if not io_facade.ask_confirm(message="Deploy this workspace?", default=True):
            raise FlowCancelationByUserException("Deployment cancelled by user")


# -----------------------------------------------------------------------------
# Distributed Training Flow
# -----------------------------------------------------------------------------


class DeployDistributedTrainingFlowDTO(BaseModel):
    """DTO for Distributed Training workspace deployment flow."""

    cluster: Optional[FlowClusterDTO] = Field(
        default=None, description="The target cluster"
    )
    model: Optional[DistributedTrainingModels] = Field(
        default=None, description="The model to train"
    )
    gradient_compression: Optional[GradientCompression] = Field(
        default=None, description="Gradient compression level"
    )
    wandb_token: StrictStr = Field(default="", description="Weights & Biases API token")
    hf_token: StrictStr = Field(default="", description="Hugging Face API token")


class DeployDistributedTrainingFlow(FlowStep[DeployDistributedTrainingFlowDTO]):
    """Flow for collecting Distributed Training workspace deployment inputs."""

    def __init__(self, service: WorkspacesService):
        self._service = service

    def _get_cluster_choices(
        self, model: DeployDistributedTrainingFlowDTO, context: FlowContext
    ) -> ChoicesSpec[FlowClusterDTO]:
        return _get_cluster_choices(self._service)

    def _get_model_choices(
        self, model: DeployDistributedTrainingFlowDTO, context: FlowContext
    ) -> ChoicesSpec[DistributedTrainingModels]:
        return ChoicesSpec[DistributedTrainingModels](
            choices=[
                DisplayChoice[DistributedTrainingModels](title=m.value, value=m)
                for m in DistributedTrainingModels
            ],
            default=DisplayChoice[DistributedTrainingModels](
                title=DistributedTrainingModels.GPT_NEO_X.value,
                value=DistributedTrainingModels.GPT_NEO_X,
            ),
        )

    def _get_compression_choices(
        self, model: DeployDistributedTrainingFlowDTO, context: FlowContext
    ) -> ChoicesSpec[GradientCompression]:
        return ChoicesSpec[GradientCompression](
            choices=[
                DisplayChoice[GradientCompression](title=c.value, value=c)
                for c in GradientCompression
            ],
            default=DisplayChoice[GradientCompression](
                title=GradientCompression.MEDIUM_COMPRESSION.value,
                value=GradientCompression.MEDIUM_COMPRESSION,
            ),
        )

    def _validate_token(self, value: str) -> bool | str:
        if len(value) > 0:
            return True
        return "Token cannot be empty"

    def execute(
        self,
        model: DeployDistributedTrainingFlowDTO,
        context: FlowContext,
        io_facade: IOFacade[BaseModel],
    ) -> None:
        flow: SequentialFlow[DeployDistributedTrainingFlowDTO] = SequentialFlow[
            DeployDistributedTrainingFlowDTO
        ](
            steps=[
                SelectRequiredStep[DeployDistributedTrainingFlowDTO, FlowClusterDTO](
                    key="cluster",
                    message="Select cluster:",
                    choices_spec=self._get_cluster_choices,
                ),
                SelectRequiredStep[
                    DeployDistributedTrainingFlowDTO, DistributedTrainingModels
                ](
                    key="model",
                    message="Select model to train:",
                    choices_spec=self._get_model_choices,
                ),
                SelectRequiredStep[
                    DeployDistributedTrainingFlowDTO, GradientCompression
                ](
                    key="gradient_compression",
                    message="Select gradient compression level:",
                    choices_spec=self._get_compression_choices,
                ),
                TextInputStep[DeployDistributedTrainingFlowDTO](
                    key="wandb_token",
                    message="Weights & Biases API token:",
                    validator=self._validate_token,
                ),
                TextInputStep[DeployDistributedTrainingFlowDTO](
                    key="hf_token",
                    message="Hugging Face API token:",
                    validator=self._validate_token,
                ),
            ]
        )
        flow.execute(model, context, io_facade)

        # Confirmation
        io_facade.display_info_message(
            message="Deploying Distributed Training workspace with the following configuration:",
            output_format=OutputFormat.TEXT,
        )
        io_facade.display_data(data=model, output_format=OutputFormat.TABLE)
        if not io_facade.ask_confirm(message="Deploy this workspace?", default=False):
            raise FlowCancelationByUserException("Deployment cancelled by user")
