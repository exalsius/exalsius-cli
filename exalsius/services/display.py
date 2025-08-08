from typing import Dict

from exalsius_api_client.models.service import Service
from exalsius_api_client.models.service_create_response import ServiceCreateResponse
from exalsius_api_client.models.service_delete_response import ServiceDeleteResponse
from exalsius_api_client.models.service_response import ServiceResponse
from exalsius_api_client.models.service_template import ServiceTemplate
from exalsius_api_client.models.services_list_response import ServicesListResponse
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from exalsius.core.base.display import BaseDisplayManager


class ServicesDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def _get_service_table(self, title: str = "Deployed Services") -> Table:
        table = Table(
            title=title,
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("ID", no_wrap=True)
        table.add_column("Name")
        table.add_column("Owner")
        table.add_column("Service Template")
        table.add_column("Created At")

        return table

    def _add_service_row(self, table: Table, service: Service):
        table.add_row(
            str(service.id),
            str(service.name),
            str(service.owner),
            str(service.template.name),
            str(service.created_at),
        )

    def display_services(self, services_response: ServicesListResponse):
        table = self._get_service_table()
        table.title = "Deployed Services"

        for service in services_response.services:
            self._add_service_row(table, service)

        self.console.print(table)

    def display_service(self, service_response: ServiceResponse):
        table = self._get_service_table("Service Details")
        self._add_service_row(table, service_response.service_deployment)
        self.console.print(table)

    def display_delete_service_message(self, service_response: ServiceDeleteResponse):
        self.print_success(f"Service {service_response.service_deployment_id} deleted")

    def display_deploy_service_message(self, service_response: ServiceCreateResponse):
        self.print_success(
            f"Service {service_response.service_deployment_id} deployment started successfully."
        )
        self.print_info(
            f"Please check the status with `exls services get {service_response.service_deployment_id}`"
        )

    def display_service_templates(self, service_templates: Dict[str, ServiceTemplate]):
        table = Table(
            title="Service Templates",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Description")

        for service_template_id, service_template in service_templates.items():
            table.add_row(
                service_template_id, service_template.name, service_template.description
            )

        self.console.print(table)

    def describe_service_template(self, service_template: ServiceTemplate):
        json_str = service_template.model_dump_json()
        self.console.print(JSON(json_str))
