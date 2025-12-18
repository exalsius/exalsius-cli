from typing import List

import typer

from exls.services.adapters.bundle import ServicesBundle
from exls.services.adapters.ui.display.render import SERVICE_VIEW
from exls.services.core.domain import Service
from exls.services.core.service import ServicesService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
from exls.shared.adapters.ui.utils import help_if_no_subcommand

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
@handle_application_layer_errors(ServicesBundle)
def list_services(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to list services of"),
):
    """
    List all services of a cluster.
    """
    bundle: ServicesBundle = ServicesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ServicesService = bundle.get_services_service()

    services: List[Service] = service.list_services(cluster_id=cluster_id)

    io_facade.display_data(
        services,
        output_format=bundle.object_output_format,
        view_context=SERVICE_VIEW,
    )


@services_app.command("get", help="Get a service of a cluster")
@handle_application_layer_errors(ServicesBundle)
def get_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to get"),
):
    """
    Get a service of a cluster.
    """
    bundle: ServicesBundle = ServicesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    services_service: ServicesService = bundle.get_services_service()

    service: Service = services_service.get_service(service_id)

    io_facade.display_data(
        service,
        output_format=bundle.object_output_format,
        view_context=SERVICE_VIEW,
    )


@services_app.command("delete", help="Delete a service of a cluster")
@handle_application_layer_errors(ServicesBundle)
def delete_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to delete"),
):
    """
    Delete a service of a cluster.
    """
    bundle: ServicesBundle = ServicesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ServicesService = bundle.get_services_service()

    deleted_service_id: str = service.delete_service(service_id)

    io_facade.display_success_message(
        f"Service {deleted_service_id} deleted successfully.",
        output_format=bundle.message_output_format,
    )
