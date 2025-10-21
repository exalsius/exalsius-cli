from typing import List

import typer

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.core.commons.factories import GatewayFactory
from exalsius.services.display import TableServicesDisplayManager
from exalsius.services.dtos import ServiceDTO, ServiceListRequestDTO
from exalsius.services.service import ServicesService
from exalsius.utils import commons as utils

services_app = typer.Typer()


def _get_services_service(ctx: typer.Context) -> ServicesService:
    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)

    gateway_factory = GatewayFactory(config, access_token)
    services_gateway = gateway_factory.create_services_gateway()

    return ServicesService(services_gateway)


@services_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage services.
    """
    utils.help_if_no_subcommand(ctx)


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
