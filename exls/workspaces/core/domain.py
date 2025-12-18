from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Literal, Optional, cast

from pydantic import BaseModel, Field, PositiveInt, StrictFloat, StrictStr


class WorkspaceClusterStatus(StrEnum):
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    READY = "READY"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceClusterStatus:
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class WorkspaceStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceStatus:
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class WorkspaceGPUVendor(StrEnum):
    AMD = "AMD"
    NVIDIA = "NVIDIA"
    NO_GPU = "NO_GPU"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceGPUVendor:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class WorkspaceAccessType(StrEnum):
    NODE_PORT = "NODE_PORT"
    INGRESS = "INGRESS"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> WorkspaceAccessType:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class WorkspaceTemplate(BaseModel):
    id_name: StrictStr = Field(..., description="The name of the workspace template")
    variables: Dict[str, Any] = Field(
        ..., description="The variables of the workspace template"
    )


class WorkspaceAccessInformation(BaseModel):
    access_type: WorkspaceAccessType = Field(..., description="The access type")
    access_protocol: str = Field(..., description="The access protocol")
    external_ips: List[str] = Field(
        default_factory=list, description="The external IPs"
    )
    port_number: int = Field(..., description="The port number")


class Workspace(BaseModel):
    id: StrictStr = Field(..., description="The ID of the workspace")
    name: StrictStr = Field(..., description="The name of the workspace")
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_name: StrictStr = Field(
        ..., description="The name of the workspace template"
    )
    status: WorkspaceStatus = Field(..., description="The status of the workspace")
    created_at: Optional[datetime] = Field(
        None, description="The creation date of the workspace"
    )
    access_information: List[WorkspaceAccessInformation] = Field(
        default_factory=lambda: cast(List[WorkspaceAccessInformation], []),
        description="The access information of the workspace",
    )


class WorkerResources(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(default=None, description="The type of the GPUs")
    gpu_vendors: Optional[StrictStr] = Field(
        default=None, description="The vendor of the GPUs"
    )
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")


class WorkerGroupResources(BaseModel):
    num_workers: int = Field(..., description="The number of workers")
    worker_resources: WorkerResources = Field(
        ..., description="The resources of the worker group"
    )


class AvailableClusterNodeResources(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    node_name: StrictStr = Field(..., description="The name of the node")
    node_endpoint: Optional[StrictStr] = Field(
        None, description="The endpoint of the node"
    )
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: WorkspaceGPUVendor = Field(..., description="The vendor of the GPU")
    gpu_count: int = Field(..., description="The count of the GPU")
    cpu_cores: int = Field(..., description="The count of the CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")


class WorkspaceCluster(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: WorkspaceClusterStatus = Field(..., description="The status of the cluster")
    available_resources: List[AvailableClusterNodeResources] = Field(
        default_factory=lambda: cast(List[AvailableClusterNodeResources], []),
        description="The available resources of the cluster",
    )

    @property
    def total_nodes(self) -> int:
        return len(self.available_resources)

    @property
    def total_gpus(self) -> int:
        return sum([resource.gpu_count for resource in self.available_resources])

    @property
    def total_amd_gpus(self) -> int:
        return sum(
            [
                resource.gpu_count
                for resource in self.available_resources
                if resource.gpu_vendor == WorkspaceGPUVendor.AMD
            ]
        )

    @property
    def total_nvidia_gpus(self) -> int:
        return sum(
            [
                resource.gpu_count
                for resource in self.available_resources
                if resource.gpu_vendor == WorkspaceGPUVendor.NVIDIA
            ]
        )

    @property
    def heterogenous(self) -> bool:
        return self.total_amd_gpus > 0 and self.total_nvidia_gpus > 0

    @property
    def available_amd_resources(self) -> List[AvailableClusterNodeResources]:
        return [
            resource
            for resource in self.available_resources
            if resource.gpu_vendor == WorkspaceGPUVendor.AMD
        ]

    @property
    def available_nvidia_resources(self) -> List[AvailableClusterNodeResources]:
        return [
            resource
            for resource in self.available_resources
            if resource.gpu_vendor == WorkspaceGPUVendor.NVIDIA
        ]

    def has_enough_resources(self, requested_resources: WorkerResources) -> bool:
        for resource in self.available_resources:
            if resource.gpu_count < requested_resources.gpu_count:
                return False
            if resource.cpu_cores < requested_resources.cpu_cores:
                return False
            if resource.memory_gb < requested_resources.memory_gb:
                return False
            if resource.storage_gb < requested_resources.storage_gb:
                return False
        return True

    def get_resource_partition_for_single_worker(
        self, num_requested_gpus: int, resource_split_tolerance: StrictFloat = 0.1
    ) -> Optional[WorkerResources]:
        for resource in self.available_resources:
            if resource.gpu_count >= num_requested_gpus:
                # These are the minimum requirements for a single node workspace
                # TODO: This is a temporary solution. We should move this to a config
                if resource.cpu_cores < 2:
                    continue
                if resource.memory_gb < 10:
                    continue
                if resource.storage_gb < 20:
                    continue

                requested_cpu_cores: int = int(
                    (resource.cpu_cores / resource.gpu_count) * num_requested_gpus
                )
                requested_memory_gb: int = int(
                    (resource.memory_gb / resource.gpu_count) * num_requested_gpus
                )
                requested_storage_gb: int = int(
                    (resource.storage_gb / resource.gpu_count) * num_requested_gpus
                )

                # We need a bit of tolerance here
                if requested_cpu_cores == resource.cpu_cores:
                    tolerance: int = int(requested_cpu_cores * resource_split_tolerance)
                    tolerance = max(tolerance, 1)
                    requested_cpu_cores -= tolerance
                if requested_memory_gb == resource.memory_gb:
                    requested_memory_gb -= int(
                        requested_memory_gb * resource_split_tolerance
                    )
                if requested_storage_gb == resource.storage_gb:
                    requested_storage_gb -= int(
                        requested_storage_gb * resource_split_tolerance
                    )
                    # We need to keep 10GB for ephemeral storage of the workspace
                    requested_storage_gb -= 10
                    # Not enough storage for the workspace
                    if requested_storage_gb < 10:
                        continue

                return WorkerResources(
                    gpu_count=num_requested_gpus,
                    gpu_type=resource.gpu_type,
                    gpu_vendors=resource.gpu_vendor.value,
                    cpu_cores=requested_cpu_cores,
                    memory_gb=requested_memory_gb,
                    storage_gb=requested_storage_gb,
                )
        return None

    def _get_resource_partition_for_worker_group(
        self,
        num_workers: int,
        gpu_vendor: str,
        resources: List[AvailableClusterNodeResources],
        resource_split_tolerance: StrictFloat,
    ) -> WorkerGroupResources:
        cpu_split: int = min(
            [
                (
                    int(resource.cpu_cores / resource.gpu_count)
                    if resource.gpu_count > 0
                    else resource.cpu_cores
                )
                for resource in resources
            ]
        )
        memory_split: int = min(
            [
                (
                    int(resource.memory_gb / resource.gpu_count)
                    if resource.gpu_count > 0
                    else resource.memory_gb
                )
                for resource in resources
            ]
        )
        storage_split: int = min(
            [
                (
                    int(resource.storage_gb / resource.gpu_count)
                    if resource.gpu_count > 0
                    else resource.storage_gb
                )
                for resource in resources
            ]
        )

        if resource_split_tolerance > 0:
            cpu_split = max(int(cpu_split * (1 - resource_split_tolerance)), 1)
            memory_split = max(int(memory_split * (1 - resource_split_tolerance)), 1)
            storage_split = max(int(storage_split * (1 - resource_split_tolerance)), 1)

        return WorkerGroupResources(
            num_workers=num_workers,
            worker_resources=WorkerResources(
                gpu_count=1,
                gpu_vendors=gpu_vendor,
                cpu_cores=cpu_split,
                memory_gb=memory_split,
                storage_gb=storage_split,
            ),
        )

    def get_resource_partition_for_worker_groups(
        self,
        num_workers: PositiveInt,
        gpu_vendor: Literal["auto", "amd", "nvidia"],
        resource_split_tolerance: StrictFloat = 0.1,
    ) -> List[WorkerGroupResources]:
        worker_group_resources_amd: WorkerGroupResources
        worker_group_resources_nvidia: WorkerGroupResources
        if gpu_vendor == "amd":
            if num_workers > self.total_amd_gpus:
                raise ValueError(
                    f"Cluster {self.name} ({self.id}) does not have enough AMD GPUs available. "
                    f"Needs at least {num_workers} GPUs. Has {self.total_amd_gpus} GPUs."
                )
            worker_group_resources_amd = self._get_resource_partition_for_worker_group(
                num_workers=num_workers,
                gpu_vendor="amd",
                resources=self.available_amd_resources,
                resource_split_tolerance=resource_split_tolerance,
            )
            return [worker_group_resources_amd]
        elif gpu_vendor == "nvidia":
            if num_workers > self.total_nvidia_gpus:
                raise ValueError(
                    f"Cluster {self.name} ({self.id}) does not have enough NVIDIA GPUs available. "
                    f"Needs at least {num_workers} GPUs. Has {self.total_nvidia_gpus} GPUs."
                )
            worker_group_resources_nvidia = (
                self._get_resource_partition_for_worker_group(
                    num_workers=num_workers,
                    gpu_vendor="nvidia",
                    resources=self.available_nvidia_resources,
                    resource_split_tolerance=resource_split_tolerance,
                )
            )
            return [worker_group_resources_nvidia]
        else:
            if num_workers > self.total_gpus:
                raise ValueError(
                    f"Cluster {self.name} ({self.id}) does not have enough GPUs available to deploy a distributed training workspace. "
                    f"Needs at least {num_workers} GPUs. Has {self.total_gpus} GPUs."
                )

            # Evenly split (proportional to availability)
            amd_workers = int(num_workers * (self.total_amd_gpus / self.total_gpus))
            nvidia_workers = num_workers - amd_workers

            # Adjust if split exceeds capacity for a specific vendor
            if amd_workers > self.total_amd_gpus:
                nvidia_workers += amd_workers - self.total_amd_gpus
                amd_workers = self.total_amd_gpus
            elif nvidia_workers > self.total_nvidia_gpus:
                amd_workers += nvidia_workers - self.total_nvidia_gpus
                nvidia_workers = self.total_nvidia_gpus

            result: List[WorkerGroupResources] = []
            if amd_workers > 0:
                result.append(
                    self._get_resource_partition_for_worker_group(
                        num_workers=amd_workers,
                        gpu_vendor="amd",
                        resources=self.available_amd_resources,
                        resource_split_tolerance=resource_split_tolerance,
                    )
                )

            if nvidia_workers > 0:
                result.append(
                    self._get_resource_partition_for_worker_group(
                        num_workers=nvidia_workers,
                        gpu_vendor="nvidia",
                        resources=self.available_nvidia_resources,
                        resource_split_tolerance=resource_split_tolerance,
                    )
                )

            return result
