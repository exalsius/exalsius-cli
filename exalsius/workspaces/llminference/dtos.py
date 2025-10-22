from typing import Optional

from pydantic import Field, PositiveInt, StrictStr

from exalsius.workspaces.dtos import DeployWorkspaceRequestDTO


class DeployLLMInferenceWorkspaceRequestDTO(DeployWorkspaceRequestDTO):
    docker_image: Optional[StrictStr] = Field(
        None, description="The docker image to use for the workspace"
    )
    huggingface_model: StrictStr = Field(
        ..., description="The HuggingFace model to use"
    )
    huggingface_token: Optional[StrictStr] = Field(
        None, description="The HuggingFace token to use"
    )
    num_model_replicas: PositiveInt = Field(
        ..., description="The number of model replicas to use"
    )
    tensor_parallel_size: PositiveInt = Field(
        ..., description="The tensor parallel size to use"
    )
    pipeline_parallel_size: PositiveInt = Field(
        ..., description="The pipeline parallel size to use"
    )
    pip_dependencies: StrictStr = Field(
        ..., description="The pip dependencies to install in the runtime environment"
    )
    gpu_per_actor: PositiveInt = Field(
        ..., description="The number of GPUs to use per actor"
    )
    cpu_per_actor: PositiveInt = Field(
        ..., description="The number of CPUs to use per actor"
    )
    memory_gb_per_actor: PositiveInt = Field(
        ..., description="The amount of memory in GB to use per actor"
    )
    ephemeral_storage_gb_per_actor: PositiveInt = Field(
        ..., description="The amount of ephemeral storage in GB to use per actor"
    )
