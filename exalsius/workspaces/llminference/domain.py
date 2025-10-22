from __future__ import annotations

from typing import ClassVar, Optional

from pydantic import Field, PositiveInt, StrictStr, model_validator

from exalsius.workspaces.domain import DeployWorkspaceParams, ResourceRequested
from exalsius.workspaces.llminference.dtos import DeployLLMInferenceWorkspaceRequestDTO


class DeployLLMInferenceWorkspaceParams(DeployWorkspaceParams):
    template_id: str = ClassVar[str]("ray-llm-service-template")
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
    ephemeral_storage_gb_per_actor: Optional[PositiveInt] = Field(
        None, description="The amount of ephemeral storage in GB to use per actor"
    )

    @model_validator(mode="after")
    def validate_resources(self) -> DeployLLMInferenceWorkspaceParams:
        gpu_count = self.resources.gpu_count
        cpu_cores = self.resources.cpu_cores
        num_model_replicas = self.num_model_replicas
        gpu_per_actor = self.gpu_per_actor
        cpu_per_actor = self.cpu_per_actor
        pipeline_parallel_size = self.pipeline_parallel_size
        tensor_parallel_size = self.tensor_parallel_size

        if gpu_count < num_model_replicas * gpu_per_actor:
            raise ValueError(
                "The total number of GPUs (`gpu-count`) must be greater than or equal to "
                "the number of model replicas (`num-model-replicas`) multiplied by "
                "the number of GPUs per replica (`gpu-per-actor`)."
            )
        if cpu_cores < num_model_replicas * cpu_per_actor:
            raise ValueError(
                "The total number of CPUs (`cpu-cores`) must be greater than or equal to "
                "the number of model replicas (`num-model-replicas`) multiplied by "
                "the number of CPUs per replica (`cpu-per-actor`)."
            )
        if (
            gpu_count
            < num_model_replicas * pipeline_parallel_size * tensor_parallel_size
        ):
            raise ValueError(
                "The total number of GPUs (`gpu-count`) must be greater than or equal to "
                "the number of model replicas (`num-model-replicas`) multiplied by "
                "the number of pipeline parallel replicas (`pipeline-parallel-size`) multiplied by "
                "the number of tensor parallel replicas (`tensor-parallel-size`)."
            )
        return self

    @classmethod
    def from_request_dto(
        cls, request_dto: DeployLLMInferenceWorkspaceRequestDTO
    ) -> DeployLLMInferenceWorkspaceParams:
        return DeployLLMInferenceWorkspaceParams(
            cluster_id=request_dto.cluster_id,
            name=request_dto.name,
            resources=ResourceRequested.from_request_dto(request_dto.resources),
            description="LLM Inference workspace",
            to_be_deleted_at=request_dto.to_be_deleted_at,
            docker_image=request_dto.docker_image,
            huggingface_model=request_dto.huggingface_model,
            huggingface_token=request_dto.huggingface_token,
            num_model_replicas=request_dto.num_model_replicas,
            tensor_parallel_size=request_dto.tensor_parallel_size,
            pipeline_parallel_size=request_dto.pipeline_parallel_size,
            pip_dependencies=request_dto.pip_dependencies,
            gpu_per_actor=request_dto.gpu_per_actor,
            cpu_per_actor=request_dto.cpu_per_actor,
            memory_gb_per_actor=request_dto.memory_gb_per_actor,
            ephemeral_storage_gb_per_actor=request_dto.ephemeral_storage_gb_per_actor,
        )
