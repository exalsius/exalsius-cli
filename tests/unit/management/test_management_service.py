from pathlib import Path
from unittest.mock import MagicMock

import pytest

from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)
from exls.management.core.ports.ports import ManagementRepository
from exls.management.core.service import ManagementService
from exls.shared.core.exceptions import ServiceError
from exls.shared.core.ports.file import FileReadPort


class TestManagementService:
    @pytest.fixture
    def mock_management_repository(self) -> MagicMock:
        return MagicMock(spec=ManagementRepository)

    @pytest.fixture
    def mock_file_read_adapter(self) -> MagicMock:
        return MagicMock(spec=FileReadPort)

    @pytest.fixture
    def service(
        self, mock_management_repository: MagicMock, mock_file_read_adapter: MagicMock
    ) -> ManagementService:
        return ManagementService(
            management_repository=mock_management_repository,
            file_read_adapter=mock_file_read_adapter,
        )

    def test_list_cluster_templates(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        expected_templates = [
            ClusterTemplate(name="template1", description="desc", k8s_version="1.20"),
            ClusterTemplate(name="template2", description="desc", k8s_version="1.21"),
        ]
        mock_management_repository.list_cluster_templates.return_value = (
            expected_templates
        )

        result = service.list_cluster_templates()

        assert result == expected_templates
        mock_management_repository.list_cluster_templates.assert_called_once()

    def test_list_credentials(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        expected_credentials = [
            Credentials(name="cred1", description="desc1"),
            Credentials(name="cred2", description="desc2"),
        ]
        mock_management_repository.list_credentials.return_value = expected_credentials

        result = service.list_credentials()

        assert result == expected_credentials
        mock_management_repository.list_credentials.assert_called_once()

    def test_list_service_templates(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        expected_templates = [
            ServiceTemplate(
                name="svc1", description="desc1", variables={"var1": "val1"}
            ),
            ServiceTemplate(
                name="svc2", description="desc2", variables={"var2": "val2"}
            ),
        ]
        mock_management_repository.list_service_templates.return_value = (
            expected_templates
        )

        result = service.list_service_templates()

        assert result == expected_templates
        mock_management_repository.list_service_templates.assert_called_once()

    def test_list_workspace_templates(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        expected_templates = [
            WorkspaceTemplate(
                name="ws1", description="desc1", variables={"var1": "val1"}
            ),
            WorkspaceTemplate(
                name="ws2", description="desc2", variables={"var2": "val2"}
            ),
        ]
        mock_management_repository.list_workspace_templates.return_value = (
            expected_templates
        )

        result = service.list_workspace_templates()

        assert result == expected_templates
        mock_management_repository.list_workspace_templates.assert_called_once()

    def test_list_ssh_keys(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        expected_keys = [
            SshKey(id="key1", name="ssh-key-1"),
            SshKey(id="key2", name="ssh-key-2"),
        ]
        mock_management_repository.list_ssh_keys.return_value = expected_keys

        result = service.list_ssh_keys()

        assert result == expected_keys
        mock_management_repository.list_ssh_keys.assert_called_once()

    def test_import_ssh_key_success(
        self,
        service: ManagementService,
        mock_management_repository: MagicMock,
        mock_file_read_adapter: MagicMock,
    ) -> None:
        name = "new-key"
        key_path = Path("/path/to/key.pub")
        file_content = "ssh-rsa AAAA..."
        new_key_id = "new-key-id"
        expected_key = SshKey(id=new_key_id, name=name)

        mock_file_read_adapter.read_file.return_value = file_content
        mock_management_repository.create_ssh_key.return_value = new_key_id
        mock_management_repository.list_ssh_keys.return_value = [
            SshKey(id="other-key", name="other"),
            expected_key,
        ]

        result = service.import_ssh_key(name=name, key_path=key_path)

        assert result == expected_key
        mock_file_read_adapter.read_file.assert_called_once_with(file_path=key_path)
        mock_management_repository.create_ssh_key.assert_called_once_with(
            name=name, base64_key_content=file_content
        )
        mock_management_repository.list_ssh_keys.assert_called_once()

    def test_import_ssh_key_failure_not_found(
        self,
        service: ManagementService,
        mock_management_repository: MagicMock,
        mock_file_read_adapter: MagicMock,
    ) -> None:
        name = "new-key"
        key_path = Path("/path/to/key.pub")
        file_content = "ssh-rsa AAAA..."
        new_key_id = "new-key-id"

        mock_file_read_adapter.read_file.return_value = file_content
        mock_management_repository.create_ssh_key.return_value = new_key_id
        # Key not in the list returned after creation
        mock_management_repository.list_ssh_keys.return_value = [
            SshKey(id="other-key", name="other")
        ]

        with pytest.raises(ServiceError) as exc_info:
            service.import_ssh_key(name=name, key_path=key_path)

        assert f"SSH key {name} was not imported" in str(exc_info.value)
        mock_file_read_adapter.read_file.assert_called_once_with(file_path=key_path)
        mock_management_repository.create_ssh_key.assert_called_once_with(
            name=name, base64_key_content=file_content
        )
        mock_management_repository.list_ssh_keys.assert_called_once()

    def test_import_ssh_key_failure_read_file(
        self,
        service: ManagementService,
        mock_file_read_adapter: MagicMock,
    ) -> None:
        name = "new-key"
        key_path = Path("/path/to/key.pub")

        # Simulate file reading error
        mock_file_read_adapter.read_file.side_effect = Exception("File not found")

        with pytest.raises(ServiceError) as exc_info:
            service.import_ssh_key(name=name, key_path=key_path)

        assert "unexpected error while importing ssh key" in str(exc_info.value)
        mock_file_read_adapter.read_file.assert_called_once_with(file_path=key_path)

    def test_import_ssh_key_failure_repository_create(
        self,
        service: ManagementService,
        mock_management_repository: MagicMock,
        mock_file_read_adapter: MagicMock,
    ) -> None:
        name = "new-key"
        key_path = Path("/path/to/key.pub")
        file_content = "ssh-rsa AAAA..."

        mock_file_read_adapter.read_file.return_value = file_content
        # Simulate repository error during creation
        mock_management_repository.create_ssh_key.side_effect = Exception("DB Error")

        with pytest.raises(ServiceError) as exc_info:
            service.import_ssh_key(name=name, key_path=key_path)

        assert "unexpected error while importing ssh key" in str(exc_info.value)
        mock_management_repository.create_ssh_key.assert_called_once()

    def test_list_ssh_keys_failure(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        # Simulate repository error during listing
        mock_management_repository.list_ssh_keys.side_effect = Exception("API Error")

        with pytest.raises(ServiceError) as exc_info:
            service.list_ssh_keys()

        assert "unexpected error while listing ssh keys" in str(exc_info.value)
        mock_management_repository.list_ssh_keys.assert_called_once()

    def test_delete_ssh_key(
        self, service: ManagementService, mock_management_repository: MagicMock
    ) -> None:
        ssh_key_id = "key-to-delete"
        expected_result = ssh_key_id
        mock_management_repository.delete_ssh_key.return_value = expected_result

        result = service.delete_ssh_key(ssh_key_id=ssh_key_id)

        assert result == expected_result
        mock_management_repository.delete_ssh_key.assert_called_once_with(ssh_key_id)
