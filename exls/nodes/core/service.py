from pathlib import Path
from typing import Dict, List, cast

from exls.nodes.core.domain import BaseNode, CloudNode, SelfManagedNode
from exls.nodes.core.ports.gateway import (
    ImportCloudNodeParameters,
    ImportSelfmanagedNodeParameters,
    INodesGateway,
)
from exls.nodes.core.ports.provider import ISshKeyProvider, NodeSshKey
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
)
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.core.service import ServiceError


class NodesService:
    def __init__(self, nodes_gateway: INodesGateway, ssh_key_provider: ISshKeyProvider):
        self.nodes_gateway: INodesGateway = nodes_gateway
        self.ssh_key_provider: ISshKeyProvider = ssh_key_provider

    @handle_service_layer_errors("listing nodes")
    def list_nodes(self, request: NodesFilterCriteria) -> List[BaseNode]:
        assert request is not None
        return self.nodes_gateway.list(request)

    @handle_service_layer_errors("getting node")
    def get_node(self, node_id: str) -> BaseNode:
        return self.nodes_gateway.get(node_id)

    @handle_service_layer_errors("deleting node")
    def delete_node(self, node_id: str) -> str:
        return self.nodes_gateway.delete(node_id)

    @handle_service_layer_errors("importing self-managed nodes")
    def import_selfmanaged_nodes(
        self, node_import_requests: List[ImportSelfmanagedNodeRequest]
    ) -> List[SelfManagedNode]:
        # Validate that the import requests are valid
        if len(node_import_requests) == 0:
            raise ServiceError(
                message="Self-managed import request must contain at least one node to import"
            )

        # Load all available SSH keys
        ssh_keys: List[NodeSshKey] = self.ssh_key_provider.list_keys()
        if len(ssh_keys) == 0:
            raise ServiceError(
                message="No SSH keys found. Please add an SSH key first using 'exls management ssh-keys add'"
            )

        # Validate that the SSH key IDs are valid
        ssh_key_map: Dict[str, NodeSshKey] = {
            ssh_key.id: ssh_key for ssh_key in ssh_keys
        }

        import_parameters: List[ImportSelfmanagedNodeParameters] = []
        for node_import_request in node_import_requests:
            ssh_key_id: str
            if isinstance(node_import_request.ssh_key, str):
                if node_import_request.ssh_key not in ssh_key_map:
                    raise ServiceError(
                        message=f"SSH key with ID {node_import_request.ssh_key} not found"
                    )
                ssh_key_id = node_import_request.ssh_key
            else:
                new_key: NodeSshKey = self._add_ssh_key(
                    name=node_import_request.ssh_key.name,
                    key_path=node_import_request.ssh_key.key_path,
                )
                ssh_key_map[new_key.id] = new_key
                ssh_key_id = new_key.id

            import_parameters.append(
                ImportSelfmanagedNodeParameters(
                    hostname=node_import_request.hostname,
                    endpoint=node_import_request.endpoint,
                    username=node_import_request.username,
                    ssh_key_id=ssh_key_id,
                )
            )

        # Import the nodes
        node_ids: List[str] = [
            self.nodes_gateway.import_selfmanaged_node(params)
            for params in import_parameters
        ]

        # Load the imported nodes
        nodes: List[SelfManagedNode] = [
            cast(SelfManagedNode, self.nodes_gateway.get(node_id))
            for node_id in node_ids
        ]

        return nodes

    def _add_ssh_key(self, name: str, key_path: Path) -> NodeSshKey:
        # Forward the request to the SSH key provider
        return self.ssh_key_provider.import_key(name=name, key_path=key_path)

    @handle_service_layer_errors("listing ssh keys")
    def list_ssh_keys(self) -> List[NodeSshKey]:
        return self.ssh_key_provider.list_keys()

    @handle_service_layer_errors("importing cloud nodes")
    def import_cloud_nodes(self, request: ImportCloudNodeRequest) -> List[CloudNode]:
        node_ids: List[str] = self.nodes_gateway.import_cloud_nodes(
            ImportCloudNodeParameters(
                hostname=request.hostname,
                offer_id=request.offer_id,
                amount=request.amount,
            )
        )
        nodes: List[CloudNode] = [
            cast(CloudNode, self.nodes_gateway.get(node_id)) for node_id in node_ids
        ]
        return nodes
