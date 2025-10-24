from typing import List

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.core.commons.factories import GatewayFactory
from exls.core.commons.service import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
)
from exls.services.display import TableServicesDisplayManager
from exls.services.dtos import ServiceDTO, ServiceListRequestDTO
from exls.services.gateway.base import ServicesGateway
from exls.services.service import ServicesService

services_app = typer.Typer()


def _get_services_service(ctx: typer.Context) -> ServicesService:
    access_token: str = get_access_token_from_ctx(ctx)
    config: AppConfig = get_config_from_ctx(ctx)

    gateway_factory: GatewayFactory = GatewayFactory(config=config)
    services_gateway: ServicesGateway = gateway_factory.create_services_gateway(
        access_token=access_token
    )

    return ServicesService(services_gateway)


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
    display_manager: TableServicesDisplayManager = TableServicesDisplayManager()

    service: ServicesService = _get_services_service(ctx)

    try:
        services: List[ServiceDTO] = service.list_services(
            ServiceListRequestDTO(cluster_id=cluster_id)
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_services(services)


@services_app.command("get", help="Get a service of a cluster")
def get_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to get"),
):
    """
    Get a service of a cluster.
    """
    display_manager: TableServicesDisplayManager = TableServicesDisplayManager()

    service: ServicesService = _get_services_service(ctx)

    try:
        service_obj: ServiceDTO = service.get_service(service_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_service(service_obj)


@services_app.command("delete", help="Delete a service of a cluster")
def delete_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to delete"),
):
    """
    Delete a service of a cluster.
    """
    display_manager: TableServicesDisplayManager = TableServicesDisplayManager()

    service: ServicesService = _get_services_service(ctx)

    try:
        deleted_service_id: str = service.delete_service(service_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(
        f"Service {deleted_service_id} deleted successfully."
    )
