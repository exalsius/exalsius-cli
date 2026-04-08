from exls.management.core.domain import (
    SshKey,
    WorkspaceTemplate,
)


class TestWorkspaceTemplate:
    def test_create_valid(self):
        """Test creating a WorkspaceTemplate with valid data."""
        template = WorkspaceTemplate(
            name="dev-env",
            description="Development environment",
            variables={"size": "large", "region": "us-east-1"},
        )
        assert template.name == "dev-env"
        assert template.description == "Development environment"
        assert template.variables == {"size": "large", "region": "us-east-1"}


class TestSshKey:
    def test_create_valid(self):
        """Test creating an SshKey with valid data."""
        key = SshKey(id="key-123", name="my-laptop-key")
        assert key.id == "key-123"
        assert key.name == "my-laptop-key"
