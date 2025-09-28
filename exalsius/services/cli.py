from typing import List

import typer
from exalsius_api_client.models.service import Service

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.services.display import TableServicesDisplayManager
from exalsius.services.service import ServicesService
from exalsius.utils import commons as utils

services_app = typer.Typer()


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

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ServicesService = ServicesService(config, access_token)

    try:
        services: List[Service] = service.list_services(cluster_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
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

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service_service: ServicesService = ServicesService(config, access_token)

    try:
        service: Service = service_service.get_service(service_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)

    display_manager.display_service(service)


@services_app.command("delete", help="Delete a service of a cluster")
def delete_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to delete"),
):
    """
    Delete a service of a cluster.
    """
    display_manager: TableServicesDisplayManager = TableServicesDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service_service: ServicesService = ServicesService(config, access_token)

    try:
        deleted_service_id: str = service_service.delete_service(service_id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)

    display_manager.display_success(
        f"Service {deleted_service_id} deleted successfully."
    )
