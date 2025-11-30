from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Union

from pydantic import BaseModel, Field, StrictStr


class NodesSshKeySpecificationDTO(BaseModel):
    name: StrictStr = Field(default="", description="The name of the SSH key")
    key_path: Path = Field(default=Path(""), description="The path to the SSH key file")


class NodesSshKeyDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the SSH key")
    name: StrictStr = Field(..., description="The name of the SSH key")


class ImportSelfmanagedNodeRequestDTO(BaseModel):
    hostname: StrictStr = Field(default="", description="The hostname of the node")
    endpoint: StrictStr = Field(default="", description="The endpoint of the node")
    username: StrictStr = Field(default="", description="The username of the node")
    ssh_key: Optional[Union[NodesSshKeyDTO, NodesSshKeySpecificationDTO]] = Field(
        default=None, description="The SSH key to use"
    )


class ImportSelfmanagedNodeRequestListDTO(BaseModel):
    nodes: Sequence[ImportSelfmanagedNodeRequestDTO] = Field(
        default=[], description="The list of nodes to import"
    )


class ImportCloudNodeRequestDTO(BaseModel):
    hostname: str = Field(..., description="The hostname of the node")
    offer_id: str = Field(..., description="The ID of the offer to use")
    amount: int = Field(..., description="The amount of nodes to import")


class NodeImportFailureDTO(BaseModel):
    hostname: StrictStr = Field(..., description="The hostname of the node")
    error_message: StrictStr = Field(..., description="The error message that occurred")
