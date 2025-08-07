# @app.command("list-services", help="List all services of a cluster")
# def list_services(
#     ctx: typer.Context,
#     cluster_id: str = typer.Argument(help="The ID of the cluster to list services of"),
# ):
#     """
#     List all services of a cluster.
#     """
#     console = Console(theme=custom_theme)
#     display_manager = ClustersDisplayManager(console)

#     access_token: str = utils.get_access_token_from_ctx(ctx)
#     config: AppConfig = utils.get_config_from_ctx(ctx)
#     service: ClustersService = ClustersService(config, access_token)

#     try:
#         cluster_services_response = service.get_cluster_services(cluster_id)
#     except ServiceError as e:
#         display_manager.print_error(e.message)
#         raise typer.Exit(1)

#     if not cluster_services_response.services_deployments:
#         display_manager.print_info("No services deployed to this cluster.")
#         raise typer.Exit()

#     display_manager.display_cluster_services(cluster_services_response)
