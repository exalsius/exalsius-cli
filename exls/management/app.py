from pathlib import Path
from typing import List, Optional

import typer

from exls.management.adapters.bundel import ManagementBundle
from exls.management.adapters.dtos import (
    ClusterTemplateDTO,
    CredentialsDTO,
    ImportSshKeyRequestDTO,
    ServiceTemplateDTO,
    SshKeyDTO,
    WorkspaceTemplateDTO,
)
from exls.management.adapters.ui.display.display import IOManagementFacade
from exls.management.adapters.ui.flows.import_ssh_key import ImportSshKeyFlow
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
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.flow.flow import FlowContext
from exls.shared.adapters.ui.utils import (
    called_with_any_user_input,
    help_if_no_subcommand,
)

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


@cluster_templates_app.command("list", help="List all available cluster templates.")
@handle_application_layer_errors(ManagementBundle)
def list_cluster_templates(
    ctx: typer.Context,
):
    """List all cluster templates."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()
    domain_cluster_templates: List[ClusterTemplate] = service.list_cluster_templates()
    dto_cluster_templates: List[ClusterTemplateDTO] = [
        cluster_template_dto_from_domain(domain=cluster_template)
        for cluster_template in domain_cluster_templates
    ]

    io_facade.display_data(
        dto_cluster_templates, output_format=bundle.object_output_format
    )


@credentials_app.command("list", help="List all available credentials")
@handle_application_layer_errors(ManagementBundle)
def list_credentials(ctx: typer.Context):
    """List all available credentials."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()

    domain_credentials: List[Credentials] = service.list_credentials()
    dto_credentials: List[CredentialsDTO] = [
        credentials_dto_from_domain(domain=credential)
        for credential in domain_credentials
    ]

    io_facade.display_data(dto_credentials, output_format=bundle.object_output_format)


@service_templates_app.command("list", help="List all available service templates")
@handle_application_layer_errors(ManagementBundle)
def list_service_templates(
    ctx: typer.Context,
):
    """List all available service templates."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()

    domain_service_templates: List[ServiceTemplate] = service.list_service_templates()
    dto_service_templates: List[ServiceTemplateDTO] = [
        service_template_dto_from_domain(domain=service_template)
        for service_template in domain_service_templates
    ]

    io_facade.display_data(
        dto_service_templates, output_format=bundle.object_output_format
    )


@workspace_templates_app.command("list", help="List all available workspace templates")
@handle_application_layer_errors(ManagementBundle)
def list_workspace_templates(
    ctx: typer.Context,
):
    """List all available workspace templates."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()

    domain_workspace_templates: List[WorkspaceTemplate] = (
        service.list_workspace_templates()
    )
    dto_workspace_templates: List[WorkspaceTemplateDTO] = [
        workspace_template_dto_from_domain(domain=workspace_template)
        for workspace_template in domain_workspace_templates
    ]

    io_facade.display_data(
        dto_workspace_templates, output_format=bundle.object_output_format
    )


@ssh_keys_app.command("list", help="List all available SSH keys")
@handle_application_layer_errors(ManagementBundle)
def list_ssh_keys(
    ctx: typer.Context,
):
    """List all available SSH keys."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()

    domain_ssh_keys: List[SshKey] = service.list_ssh_keys()
    dto_ssh_keys: List[SshKeyDTO] = [
        ssh_key_dto_from_domain(domain=ssh_key) for ssh_key in domain_ssh_keys
    ]

    io_facade.display_data(dto_ssh_keys, output_format=bundle.object_output_format)


@ssh_keys_app.command("import", help="Import a new SSH key")
@handle_application_layer_errors(ManagementBundle)
def import_ssh_key(
    ctx: typer.Context,
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Name for the SSH key"
    ),
    key_path: Optional[Path] = typer.Option(
        None, "--key-path", "-k", help="Path to the SSH private key file"
    ),
):
    """Import a new SSH key to the management cluster."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()

    add_ssh_key_request: ImportSshKeyRequestDTO = ImportSshKeyRequestDTO()
    if not called_with_any_user_input(ctx):
        add_ssh_key_flow: ImportSshKeyFlow = bundle.get_import_ssh_key_flow()
        add_ssh_key_flow.execute(add_ssh_key_request, FlowContext(), io_facade)
    else:
        if not name or not key_path:
            io_facade.display_error_message(
                message="Name and key path are required",
                output_format=bundle.message_output_format,
            )
            raise typer.Exit(1)

        add_ssh_key_request.name = name
        add_ssh_key_request.key_path = key_path

    domain_ssh_key: SshKey = service.import_ssh_key(
        name=add_ssh_key_request.name, key_path=add_ssh_key_request.key_path
    )
    dto_ssh_key: SshKeyDTO = ssh_key_dto_from_domain(domain=domain_ssh_key)

    io_facade.display_data(dto_ssh_key, output_format=bundle.object_output_format)


@ssh_keys_app.command("delete", help="Delete an SSH key")
@handle_application_layer_errors(ManagementBundle)
def delete_ssh_key(
    ctx: typer.Context,
    ssh_key_id: str = typer.Argument(..., help="ID of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    bundle: ManagementBundle = ManagementBundle(ctx)
    io_facade: IOManagementFacade = bundle.get_io_facade()
    service: ManagementService = bundle.get_management_service()

    deleted_ssh_key_id: str = service.delete_ssh_key(ssh_key_id)

    io_facade.display_success_message(
        f"SSH key {deleted_ssh_key_id} deleted successfully",
        output_format=bundle.message_output_format,
    )
