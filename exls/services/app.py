from typing import List

import typer

from exls.services.adapters.bundle import ServicesBundle
from exls.services.adapters.dtos import ServiceDTO
from exls.services.adapters.ui.display.display import ServicesInteractionManager
from exls.services.adapters.ui.mappers import service_dto_from_domain
from exls.services.core.domain import Service
from exls.services.core.service import ServicesService
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.service import ServiceError

services_app = typer.Typer()


@services_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage services.
    """
    help_if_no_subcommand(ctx)


@services_app.command("list", help="List all services of a cluster")
def list_services(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to list services of"),
):
    """
    List all services of a cluster.
    """
    bundle: ServicesBundle = ServicesBundle(ctx)
    display_manager: ServicesInteractionManager = bundle.get_interaction_manager()
    service: ServicesService = bundle.get_services_service()

    try:
        domain_services: List[Service] = service.list_services(cluster_id=cluster_id)
        dto_services: List[ServiceDTO] = [
            service_dto_from_domain(domain=s) for s in domain_services
        ]
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(
        dto_services, output_format=bundle.object_output_format
    )


@services_app.command("get", help="Get a service of a cluster")
def get_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to get"),
):
    """
    Get a service of a cluster.
    """
    bundle: ServicesBundle = ServicesBundle(ctx)
    display_manager: ServicesInteractionManager = bundle.get_interaction_manager()
    service: ServicesService = bundle.get_services_service()

    try:
        domain_service: Service = service.get_service(service_id)
        dto_service: ServiceDTO = service_dto_from_domain(domain=domain_service)
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_data(dto_service, output_format=bundle.object_output_format)


@services_app.command("delete", help="Delete a service of a cluster")
def delete_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to delete"),
):
    """
    Delete a service of a cluster.
    """
    bundle: ServicesBundle = ServicesBundle(ctx)
    display_manager: ServicesInteractionManager = bundle.get_interaction_manager()
    service: ServicesService = bundle.get_services_service()

    try:
        deleted_service_id: str = service.delete_service(service_id)
    except ServiceError as e:
        display_manager.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    display_manager.display_success_message(
        f"Service {deleted_service_id} deleted successfully.",
        output_format=bundle.message_output_format,
    )
