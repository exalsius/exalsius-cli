import pytest
from pydantic import ValidationError

from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)


class TestClusterTemplate:
    def test_create_valid_full(self):
        """Test creating a ClusterTemplate with all fields."""
        template = ClusterTemplate(
            name="test-cluster",
            description="A test cluster template",
            k8s_version="1.29.0",
        )
        assert template.name == "test-cluster"
        assert template.description == "A test cluster template"
        assert template.k8s_version == "1.29.0"


class TestCredentials:
    def test_create_valid_full(self):
        """Test creating Credentials with all fields."""
        creds = Credentials(
            name="aws-creds",
            description="AWS production credentials",
        )
        assert creds.name == "aws-creds"
        assert creds.description == "AWS production credentials"

    def test_create_invalid_type(self):
        """Test type validation."""
        with pytest.raises(ValidationError):
            Credentials(name=123, description="test-description")  # type: ignore


class TestServiceTemplate:
    def test_create_valid(self):
        """Test creating a ServiceTemplate with valid data."""
        template = ServiceTemplate(
            name="nginx",
            description="Nginx server",
            variables={"port": 80, "image": "nginx:latest"},
        )
        assert template.name == "nginx"
        assert template.description == "Nginx server"
        assert template.variables == {"port": 80, "image": "nginx:latest"}

    def test_create_invalid_variables_type(self):
        """Test that variables must be a dict."""
        with pytest.raises(ValidationError):
            ServiceTemplate(
                name="nginx",
                description="desc",
                variables="not-a-dict",  # type: ignore
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
