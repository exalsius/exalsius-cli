from typing import Literal, Optional

from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.workspaces.models import WorkspaceBaseTemplateDTO


class DilocoTrainerVariablesDTO(BaseSettings):
    model: str = Field(..., description="The model to train")
    dataset: str = Field(..., description="The dataset to use for training")
    local_steps: int = Field(
        ..., description="The number of local steps", alias="localSteps"
    )
    lr: float = Field(..., description="The learning rate")
    outer_lr: float = Field(..., description="The outer learning rate", alias="outerLr")
    warmup_steps: int = Field(
        ..., description="The number of warmup steps", alias="warmupSteps"
    )
    total_steps: int = Field(
        ..., description="The total number of steps", alias="totalSteps"
    )
    per_device_train_batch_size: int = Field(
        ...,
        description="The per device train batch size",
        alias="perDeviceTrainBatchSize",
    )
    batch_size: int = Field(..., description="The batch size", alias="batchSize")
    optim_method: str = Field(
        ..., description="The optimization method", alias="optimMethod"
    )
    quantization: bool = Field(False, description="Whether to use quantization")
    checkpoint_path: str = Field(
        ...,
        description="The path to save checkpoints",
        alias="checkpointPath",
    )
    checkpoint_interval: int = Field(
        ..., description="The checkpoint interval", alias="checkpointInterval"
    )
    device: str = Field(..., description="The device to use for training")
    heterogeneous: bool = Field(
        False, description="Whether the training is heterogeneous"
    )
    compression_decay: float = Field(
        ..., description="The compression decay", alias="compressionDecay"
    )
    compression_topk: int = Field(
        ..., description="The compression topk", alias="compressionTopk"
    )
    experiment_description: str = Field(
        ...,
        description="The experiment description",
        alias="experimentDescription",
    )
    experiment_tags: list[str] = Field(
        ...,
        description="The experiment tags",
        alias="experimentTags",
    )
    seed: int = Field(..., description="The random seed")
    wandb_logging: bool = Field(
        False, description="Whether to log to wandb", alias="wandbLogging"
    )
    wandb_user_key: Optional[str] = Field(
        None, description="The wandb user key", alias="wandbUserKey"
    )
    wandb_project_name: Optional[str] = Field(
        None, description="The wandb project name", alias="wandbProjectName"
    )
    wandb_group: Optional[str] = Field(
        None, description="The wandb group", alias="wandbGroup"
    )
    huggingface_token: Optional[str] = Field(
        None, description="The huggingface token", alias="huggingfaceToken"
    )

    model_config = SettingsConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="ignore"
    )


class DilocoWorkspaceVariablesDTO(BaseSettings):
    deployment_name: str = Field(..., description="The name of the deployment")
    nodes: int = Field(..., description="The number of nodes")
    ephemeral_storage_gb: int = Field(
        ...,
        description="The amount of ephemeral storage in GB to add to the workspace pod",
    )

    diloco: DilocoTrainerVariablesDTO = Field(
        ..., description="The variables of the diloco trainer"
    )

    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class DilocoWorkspaceTemplateDTO(WorkspaceBaseTemplateDTO):
    name: Literal["diloco-workspace-template"] = "diloco-workspace-template"
    variables: DilocoWorkspaceVariablesDTO = Field(
        ..., description="The variables of the diloco workspace template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = WorkspaceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True, exclude_none=True),
        )
        return template
