from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, StrictStr


class Offer(BaseModel):
    """Domain object representing an offer."""

    id: StrictStr = Field(..., description="The ID of the offer")
    provider: StrictStr = Field(..., description="The cloud provider")
    instance_type: StrictStr = Field(..., description="The instance type")
    price_per_hour: PositiveFloat = Field(..., description="The price per hour")
    gpu_type: StrictStr = Field(..., description="The type of GPU")
    gpu_count: PositiveInt = Field(..., description="The number of GPUs")
    gpu_memory_mib: PositiveInt = Field(..., description="The GPU memory in MiB")
    num_vcpus: PositiveInt = Field(..., description="The number of vCPUs")
    main_memory_mib: PositiveInt = Field(..., description="The main memory in MiB")
    region: StrictStr = Field(..., description="The region")
