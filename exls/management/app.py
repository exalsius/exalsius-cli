from pathlib import Path
from typing import List

import typer

from exls.management.adapters.bundel import ManagementBundle
from exls.management.adapters.dtos import (
    ClusterTemplateDTO,
    CredentialsDTO,
    ServiceTemplateDTO,
    SshKeyDTO,
    WorkspaceTemplateDTO,
)
from exls.management.adapters.ui.display.display import ManagementInteractionManager
from exls.management.adapters.ui.mapper import (
    cluster_template_dto_from_domain,
    credentials_dto_from_domain,
    service_template_dto_from_domain,
    ssh_key_dto_from_domain,
    workspace_template_dto_from_domain,
)
from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)
from exls.management.core.service import ManagementService
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.service import ServiceError

management_app = typer.Typer()

credentials_app = typer.Typer()
cluster_templates_app = typer.Typer()
service_templates_app = typer.Typer()
workspace_templates_app = typer.Typer()
ssh_keys_app = typer.Typer()

management_app.add_typer(credentials_app, name="credentials")
management_app.add_typer(cluster_templates_app, name="cluster-templates")
management_app.add_typer(service_templates_app, name="service-templates")
management_app.add_typer(workspace_templates_app, name="workspace-templates")
management_app.add_typer(ssh_keys_app, name="ssh-keys")


@management_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage the management resources.
    """
    help_if_no_subcommand(ctx)


@cluster_templates_app.command("list", help="List all cluster templates.")
def list_cluster_templates(
    ctx: typer.Context,
):
    """List all cluster templates."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()
    try:
        domain_cluster_templates: List[ClusterTemplate] = (
            service.list_cluster_templates()
        )
        dto_cluster_templates: List[ClusterTemplateDTO] = [
            cluster_template_dto_from_domain(domain=cluster_template)
            for cluster_template in domain_cluster_templates
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(
        dto_cluster_templates, output_format=bundle.object_output_format
    )


@credentials_app.command("list", help="List all available credentials")
def list_credentials(ctx: typer.Context):
    """List all available credentials."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()
    try:
        domain_credentials: List[Credentials] = service.list_credentials()
        dto_credentials: List[CredentialsDTO] = [
            credentials_dto_from_domain(domain=credential)
            for credential in domain_credentials
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(
        dto_credentials, output_format=bundle.object_output_format
    )


@service_templates_app.command("list", help="List all available service templates")
def list_service_templates(
    ctx: typer.Context,
):
    """List all available service templates."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()

    try:
        domain_service_templates: List[ServiceTemplate] = (
            service.list_service_templates()
        )
        dto_service_templates: List[ServiceTemplateDTO] = [
            service_template_dto_from_domain(domain=service_template)
            for service_template in domain_service_templates
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(
        dto_service_templates, output_format=bundle.object_output_format
    )


@workspace_templates_app.command("list", help="List all available workspace templates")
def list_workspace_templates(
    ctx: typer.Context,
):
    """List all available workspace templates."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()
    try:
        domain_workspace_templates: List[WorkspaceTemplate] = (
            service.list_workspace_templates()
        )
        dto_workspace_templates: List[WorkspaceTemplateDTO] = [
            workspace_template_dto_from_domain(domain=workspace_template)
            for workspace_template in domain_workspace_templates
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(
        dto_workspace_templates, output_format=bundle.object_output_format
    )


@ssh_keys_app.command("list", help="List all available SSH keys")
def list_ssh_keys(
    ctx: typer.Context,
):
    """List all available SSH keys."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()
    try:
        domain_ssh_keys: List[SshKey] = service.list_ssh_keys()
        dto_ssh_keys: List[SshKeyDTO] = [
            ssh_key_dto_from_domain(domain=ssh_key) for ssh_key in domain_ssh_keys
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(
        dto_ssh_keys, output_format=bundle.object_output_format
    )


@ssh_keys_app.command("add", help="Add a new SSH key")
def add_ssh_key(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name for the SSH key"),
    key_path: Path = typer.Option(
        ..., "--key-path", "-k", help="Path to the SSH private key file"
    ),
):
    """Add a new SSH key to the management cluster."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()
    try:
        domain_ssh_key: SshKey = service.add_ssh_key(name=name, key_path=key_path)
        dto_ssh_key: SshKeyDTO = ssh_key_dto_from_domain(domain=domain_ssh_key)
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(dto_ssh_key, output_format=bundle.object_output_format)


@ssh_keys_app.command("delete", help="Delete an SSH key")
def delete_ssh_key(
    ctx: typer.Context,
    ssh_key_id: str = typer.Argument(..., help="ID of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    display_manager: ManagementInteractionManager = bundle.get_interaction_manager()
    service: ManagementService = bundle.get_management_service()
    try:
        deleted_ssh_key_id: str = service.delete_ssh_key(ssh_key_id)
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_success_message(
        f"SSH key {deleted_ssh_key_id} deleted successfully",
        output_format=bundle.message_output_format,
    )
