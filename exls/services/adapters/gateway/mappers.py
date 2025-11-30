from exalsius_api_client.models.service import Service as SdkService

from exls.services.core.domain import Service


def service_from_sdk(sdk_model: SdkService) -> Service:
    return Service(
        id=sdk_model.id or "",
        name=sdk_model.name,
        cluster_id=sdk_model.cluster_id,
        service_template=sdk_model.template.name,
        created_at=sdk_model.created_at,
    )
