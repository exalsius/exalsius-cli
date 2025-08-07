# def display_cluster_services(
#     self, cluster_services_response: ClusterServicesResponse
# ):
#     table = Table(
#         title="Cluster Service Deployments",
#         show_header=True,
#         header_style="bold",
#         border_style="custom",
#     )
#     table.add_column("Service Name")
#     table.add_column("Values")

#     for service_deployment in cluster_services_response.services_deployments:
#         table.add_row(
#             str(service_deployment.service_name),
#             str(service_deployment.values),
#         )

#     self.console.print(table)
