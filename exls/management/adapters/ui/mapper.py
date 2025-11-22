from exls.management.adapters.dtos import (
    ClusterTemplateDTO,
    CredentialsDTO,
    ServiceTemplateDTO,
    SshKeyDTO,
    WorkspaceTemplateDTO,
)
from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)


def cluster_template_dto_from_domain(domain: ClusterTemplate) -> ClusterTemplateDTO:
    """Helper function to convert a cluster template domain to a DTO node."""
    return ClusterTemplateDTO(
        name=domain.name,
        description=domain.description,
        k8s_version=domain.k8s_version,
    )


def credentials_dto_from_domain(domain: Credentials) -> CredentialsDTO:
    """Helper function to convert a credentials domain to a DTO node."""
    return CredentialsDTO(
        name=domain.name,
        description=domain.description,
    )


def service_template_dto_from_domain(domain: ServiceTemplate) -> ServiceTemplateDTO:
    """Helper function to convert a service template domain to a DTO node."""
    return ServiceTemplateDTO(
        name=domain.name,
        description=domain.description,
        variables=", ".join(domain.variables) if domain.variables else "",
    )


def workspace_template_dto_from_domain(
    domain: WorkspaceTemplate,
) -> WorkspaceTemplateDTO:
    """Helper function to convert a workspace template domain to a DTO node."""
    return WorkspaceTemplateDTO(
        name=domain.name,
        description=domain.description or "",
        variables=domain.variables if domain.variables else {},
    )


def ssh_key_dto_from_domain(domain: SshKey) -> SshKeyDTO:
    """Helper function to convert a SSH key domain to a DTO node."""
    return SshKeyDTO(
        id=domain.id,
        name=domain.name,
    )
