from typing import List

import typer

from exls.clusters.adapters.bundle import ClustersBundle
from exls.clusters.core.domain import ClusterSummary
from exls.clusters.core.service import ClustersService
from exls.services.adapters.bundle import ServicesBundle
from exls.services.adapters.ui.display.render import SERVICE_VIEW
from exls.services.core.domain import Service
from exls.services.core.service import ServicesService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.facade.facade import IOBaseModelFacade
from exls.shared.adapters.ui.utils import (
    get_app_state_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
)
from exls.shared.core.resolver import (
    AmbiguousResourceError,
    ResourceNotFoundError,
    resolve_resource_id,
)

services_app = typer.Typer()


def _get_bundle(ctx: typer.Context) -> ServicesBundle:
    """Helper to instantiate the ServicesBundle from the context."""
    return ServicesBundle(get_config_from_ctx(ctx), get_app_state_from_ctx(ctx))


def _resolve_cluster_id_callback(ctx: typer.Context, value: str) -> str:
    """
    Callback to resolve a cluster name or ID to a cluster ID.
    Fetches all clusters and matches the name/ID.
    """
    try:
        clusters_bundle: ClustersBundle = ClustersBundle(
            get_config_from_ctx(ctx), get_app_state_from_ctx(ctx)
        )
        service: ClustersService = clusters_bundle.get_clusters_service()
        clusters: List[ClusterSummary] = service.list_clusters()
        return resolve_resource_id(clusters, value, "cluster")
    except (ResourceNotFoundError, AmbiguousResourceError) as e:
        raise typer.BadParameter(str(e))


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
    cluster_id: str = typer.Argument(
        help="The name or ID of the cluster to list services of",
        metavar="CLUSTER_NAME_OR_ID",
        callback=_resolve_cluster_id_callback,
    ),
):
    """
    List all services of a cluster.
    """
    bundle: ServicesBundle = _get_bundle(ctx)
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
    service_id: str = typer.Argument(
        help="The ID of the service to get",
    ),
):
    """
    Get a service of a cluster.
    """
    bundle: ServicesBundle = _get_bundle(ctx)
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
    service_id: str = typer.Argument(
        help="The ID of the service to delete",
    ),
):
    """
    Delete a service of a cluster.
    """
    bundle: ServicesBundle = _get_bundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ServicesService = bundle.get_services_service()

    deleted_service_id: str = service.delete_service(service_id)

    io_facade.display_success_message(
        f"Service {deleted_service_id} deleted successfully.",
        output_format=bundle.message_output_format,
    )
