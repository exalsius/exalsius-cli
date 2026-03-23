from pathlib import Path
from unittest.mock import MagicMock, create_autospec

from exls.management.core.domain import SshKey, SshKeyScope
from exls.management.core.service import ManagementService
from exls.nodes.adapters.provider.sshkey import ManagementDomainSshProvider


class TestManagementDomainSshProvider:
    def _make_provider(self, mock_service: MagicMock) -> ManagementDomainSshProvider:
        return ManagementDomainSshProvider(management_service=mock_service)

    def test_list_keys_maps_scope(self) -> None:
        mock_service = create_autospec(ManagementService)
        mock_service.list_ssh_keys.return_value = [
            SshKey(id="k1", name="private-key", scope=SshKeyScope.PRIVATE),
            SshKey(id="k2", name="org-key", scope=SshKeyScope.ORG),
        ]
        provider = self._make_provider(mock_service)

        result = provider.list_keys()

        assert len(result) == 2
        assert result[0].id == "k1"
        assert result[0].scope == "private"
        assert result[1].id == "k2"
        assert result[1].scope == "org"

    def test_import_key_maps_scope(self) -> None:
        mock_service = create_autospec(ManagementService)
        mock_service.import_ssh_key.return_value = SshKey(
            id="k3", name="new-org-key", scope=SshKeyScope.ORG
        )
        provider = self._make_provider(mock_service)

        result = provider.import_key(name="new-org-key", key_path=Path("/tmp/key"))

        assert result.id == "k3"
        assert result.name == "new-org-key"
        assert result.scope == "org"

    def test_get_key_returns_key_with_scope(self) -> None:
        mock_service = create_autospec(ManagementService)
        mock_service.list_ssh_keys.return_value = [
            SshKey(id="k1", name="my-key", scope=SshKeyScope.ORG),
        ]
        provider = self._make_provider(mock_service)

        result = provider.get_key(id="k1")

        assert result is not None
        assert result.scope == "org"
