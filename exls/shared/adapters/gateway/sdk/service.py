from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration


def create_api_client(backend_host: str, access_token: str) -> ApiClient:
    client_config: Configuration = Configuration(host=backend_host)
    api_client: ApiClient = ApiClient(configuration=client_config)
    api_client.set_default_header(  # type: ignore[reportUnknownMemberType]
        "Authorization", f"Bearer {access_token}"
    )
    return api_client
