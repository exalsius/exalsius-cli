from typing import Annotated

import typer
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from rich.console import Console

from exalsius.config import AppConfig
from exalsius.core.commons.models import ServiceError
from exalsius.services.display import ServicesDisplayManager
from exalsius.services.models import ServiceTemplates
from exalsius.services.service import ServicesService
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    cluster: Annotated[
        str | None,
        typer.Option("--cluster", "-c", help="Cluster to use."),
    ] = None,
):
    """
    List and manage services of a cluster.
    """
    utils.help_if_no_subcommand(ctx)


@app.command("list", help="List all services of a cluster")
def list_services(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to list services of"),
):
    """
    List all services of a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ServicesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ServicesService = ServicesService(config, access_token)

    try:
        services_response = service.list_services(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    if not services_response.services:
        display_manager.print_info("No services deployed to this cluster.")
        raise typer.Exit()

    display_manager.display_services(services_response)


@app.command("get", help="Get a service of a cluster")
def get_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to get"),
):
    """
    Get a service of a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ServicesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ServicesService = ServicesService(config, access_token)

    try:
        service_response = service.get_service(service_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_service(service_response)


@app.command("delete", help="Delete a service of a cluster")
def delete_service(
    ctx: typer.Context,
    service_id: str = typer.Argument(help="The ID of the service to delete"),
):
    """
    Delete a service of a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ServicesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ServicesService = ServicesService(config, access_token)

    try:
        service_response = service.delete_service(service_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_delete_service_message(service_response)


@app.command("list-templates", help="List all service templates")
def list_service_templates(
    ctx: typer.Context,
):
    """
    List all service templates.
    """
    console = Console(theme=custom_theme)
    display_manager = ServicesDisplayManager(console)

    display_manager.display_service_templates(
        {f.value: f.create_service_template() for f in ServiceTemplates}
    )


@app.command("describe-template", help="Describe a service template")
def describe_service_template(
    ctx: typer.Context,
    service_template: ServiceTemplates = typer.Argument(
        help="The service template factory to use",
    ),
):
    """
    Describe a service template.
    """
    console = Console(theme=custom_theme)
    display_manager = ServicesDisplayManager(console)

    display_manager.describe_service_template(
        service_template.create_service_template()
    )


@app.command("deploy", help="Deploy a service to a cluster")
def deploy_service(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    service_template: ServiceTemplates = typer.Argument(
        help="The service template factory to use",
    ),
    name: str = typer.Option(
        utils.generate_random_name(prefix="exls-service"),
        "--name",
        "-n",
        help="The name of the service to deploy. If not provided, a random name will be generated.",
        show_default=False,
    ),
):
    """
    Deploy a service to a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ServicesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ServicesService = ServicesService(config, access_token)

    try:
        service_response: ServiceCreateResponse = service.deploy_service(
            cluster_id=cluster_id,
            name=name,
            service_template=service_template,
        )
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_deploy_service_message(service_response)
