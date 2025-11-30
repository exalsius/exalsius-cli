from pathlib import Path
from typing import List

from exls.management.core.domain import SshKey
from exls.management.core.service import ManagementService
from exls.nodes.core.ports.provider import ISshKeyProvider, NodeSshKey


class ManagementDomainSshProvider(ISshKeyProvider):
    def __init__(self, management_service: ManagementService):
        self.management_service: ManagementService = management_service

    def list_keys(self) -> List[NodeSshKey]:
        ssh_keys: List[SshKey] = self.management_service.list_ssh_keys()
        node_ssh_keys: List[NodeSshKey] = []
        for ssh_key in ssh_keys:
            node_ssh_keys.append(NodeSshKey(id=ssh_key.id, name=ssh_key.name))
        return node_ssh_keys

    def import_key(self, name: str, key_path: Path) -> NodeSshKey:
        domain_ssh_key: SshKey = self.management_service.import_ssh_key(
            name=name, key_path=key_path
        )
        return NodeSshKey(id=domain_ssh_key.id, name=domain_ssh_key.name)
