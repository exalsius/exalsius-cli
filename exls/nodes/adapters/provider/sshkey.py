from pathlib import Path
from typing import List

from typing_extensions import Optional

from exls.management.core.domain import SshKey
from exls.management.core.service import ManagementService
from exls.nodes.core.ports.provider import NodeSshKey, SshKeyProvider


class ManagementDomainSshProvider(SshKeyProvider):
    def __init__(self, management_service: ManagementService):
        self.management_service: ManagementService = management_service

    def list_keys(self) -> List[NodeSshKey]:
        ssh_keys: List[SshKey] = self.management_service.list_ssh_keys()
        node_ssh_keys: List[NodeSshKey] = []
        for ssh_key in ssh_keys:
            node_ssh_keys.append(NodeSshKey(id=ssh_key.id, name=ssh_key.name))
        return node_ssh_keys

    def get_key(self, id: str) -> Optional[NodeSshKey]:
        ssh_keys: List[NodeSshKey] = self.list_keys()
        for ssh_key in ssh_keys:
            if ssh_key.id == id:
                return ssh_key
        return None

    def import_key(self, name: str, key_path: Path) -> NodeSshKey:
        domain_ssh_key: SshKey = self.management_service.import_ssh_key(
            name=name, key_path=key_path
        )
        return NodeSshKey(id=domain_ssh_key.id, name=domain_ssh_key.name)
