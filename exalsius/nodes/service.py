from typing import Any, List, Optional

from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.node_import_response import NodeImportResponse
from exalsius_api_client.models.node_response import NodeResponse
from exalsius_api_client.models.nodes_list_response import NodesListResponse

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.nodes.commands import (
    DeleteNodeCommand,
    GetNodeCommand,
    ImportFromOfferCommand,
    ImportSSHNodeCommand,
    ListNodesCommand,
)
from exalsius.nodes.models import (
    CloudProvider,
    NodesDeleteRequestDTO,
    NodesGetRequestDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    NodesListRequestDTO,
    NodeType,
)

NODES_API_ERROR_TYPE: str = "NodesApiError"


class NodeService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.nodes_api: NodesApi = NodesApi(self.api_client)

    def _execute_command(self, command: BaseCommand) -> Any:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                message=f"api error while executing command {command.__class__.__name__}: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=NODES_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=NODES_API_ERROR_TYPE,
            )

    def list_nodes(
        self, node_type: Optional[NodeType], provider: Optional[CloudProvider]
    ) -> List[BaseNode]:
        req: NodesListRequestDTO = NodesListRequestDTO(
            api=self.nodes_api,
            node_type=node_type,
            provider=provider,
        )
        response: NodesListResponse = self._execute_command(
            ListNodesCommand(request=req)
        )
        nodes: List[BaseNode] = [
            node.actual_instance
            for node in response.nodes
            if node.actual_instance is not None
        ]
        return nodes

    def get_node(self, node_id: str) -> BaseNode:
        req: NodesGetRequestDTO = NodesGetRequestDTO(
            api=self.nodes_api,
            node_id=node_id,
        )
        response: NodeResponse = self._execute_command(GetNodeCommand(request=req))
        if response.actual_instance is None:
            raise ServiceError(
                f"Response for node {node_id} contains no actual instance. This is unexpected."
            )
        return response.actual_instance

    def delete_node(self, node_id: str) -> None:
        req: NodesDeleteRequestDTO = NodesDeleteRequestDTO(
            api=self.nodes_api,
            node_id=node_id,
        )
        self._execute_command(DeleteNodeCommand(request=req))

    def import_ssh_node(
        self, hostname: str, endpoint: str, username: str, ssh_key_id: str
    ) -> str:
        req: NodesImportSSHRequestDTO = NodesImportSSHRequestDTO(
            api=self.nodes_api,
            hostname=hostname,
            endpoint=endpoint,
            username=username,
            ssh_key_id=ssh_key_id,
        )
        response: NodeImportResponse = self._execute_command(
            ImportSSHNodeCommand(request=req)
        )
        return response.node_ids[0]

    def import_from_offer(self, hostname: str, offer_id: str, amount: int) -> List[str]:
        req: NodesImportFromOfferRequestDTO = NodesImportFromOfferRequestDTO(
            api=self.nodes_api,
            hostname=hostname,
            offer_id=offer_id,
            amount=amount,
        )
        response: NodeImportResponse = self._execute_command(
            ImportFromOfferCommand(request=req)
        )
        return response.node_ids
