from exls.services.adapters.dtos import ServiceDTO
from exls.services.core.domain import Service


def service_dto_from_domain(domain: Service) -> ServiceDTO:
    return ServiceDTO(
        id=domain.id,
        name=domain.name,
        cluster_id=domain.cluster_id,
        template_name=domain.service_template,
        created_at=domain.created_at,
    )
