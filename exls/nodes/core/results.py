from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.nodes.core.domain import SelfManagedNode
from exls.nodes.core.requests import ImportSelfmanagedNodeRequest


class DeleteNodeIssue(BaseModel):
    node_id: StrictStr = Field(..., description="The node ID")
    error_message: StrictStr = Field(..., description="The error message that occurred")


class DeleteNodesResult(BaseModel):
    deleted_node_ids: List[StrictStr] = Field(..., description="The deleted node IDs")
    issues: Optional[List[DeleteNodeIssue]] = Field(
        default=None, description="List of deletion issues encountered"
    )

    @property
    def is_success(self) -> bool:
        return self.issues is None or len(self.issues) == 0


class ImportSelfmanagedNodeIssue(BaseModel):
    """Domain object representing the issue of importing a node."""

    node_import_request: ImportSelfmanagedNodeRequest = Field(
        ..., description="The node import request that was imported"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")


class ImportSelfmanagedNodesResult(BaseModel):
    """Domain object representing the issues of importing multiple nodes."""

    imported_nodes: List[SelfManagedNode] = Field(
        ..., description="The nodes that were imported"
    )
    issues: List[ImportSelfmanagedNodeIssue] = Field(
        ..., description="The issues that occurred"
    )

    @property
    def is_success(self) -> bool:
        return len(self.issues) == 0
