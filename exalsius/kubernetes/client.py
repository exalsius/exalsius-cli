from typing import Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError


class KubernetesClientError(Exception):
    """Base exception for Kubernetes client errors."""

    pass


class KubernetesClient:
    """
    Base Kubernetes client class that handles connection and provides common functionality.
    This class serves as a foundation for more specific Kubernetes operation classes.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the Kubernetes client.

        Args:
            config_file: Optional path to kubeconfig file. If None, uses default config.
        """
        self._initialize_client(config_file)

    def _initialize_client(self, config_file: Optional[str] = None) -> None:
        """
        Initialize the Kubernetes client configuration.

        Args:
            config_file: Optional path to kubeconfig file.

        Raises:
            KubernetesClientError: If client initialization fails.
        """
        try:
            if config_file:
                config.load_kube_config(config_file=config_file)
            else:
                config.load_kube_config()

            self.api_client = client.ApiClient()
            self.custom_objects_api = client.CustomObjectsApi(self.api_client)
            self.core_api = client.CoreV1Api(self.api_client)

        except Exception as e:
            raise KubernetesClientError(
                f"Failed to initialize Kubernetes client: {str(e)}"
            )

    def _make_api_call(self, api_func, *args, **kwargs):
        """
        Helper method to make API calls with consistent error handling.

        Args:
            api_func: The API function to call
            *args: Positional arguments for the API function
            **kwargs: Keyword arguments for the API function

        Returns:
            The API response if successful

        Raises:
            KubernetesClientError: If the API call fails
        """
        try:
            return api_func(*args, **kwargs)
        except (ConnectionError, MaxRetryError) as e:
            raise KubernetesClientError(
                f"Failed to connect to Kubernetes API server: {str(e)}"
            )
        except ApiException as e:
            if e.status == 404:
                raise KubernetesClientError(f"Resource not found: {str(e)}")
            raise KubernetesClientError(
                f"Kubernetes API error ({e.status}): {e.reason}"
            )
        except Exception as e:
            raise KubernetesClientError(f"Unexpected error during API call: {str(e)}")

    def get_api_resources(self, group: str, version: str) -> dict:
        """
        Get available API resources for a specific API group and version.

        Args:
            group: The API group
            version: The API version

        Returns:
            Dict containing API resources information
        """
        return self._make_api_call(
            self.custom_objects_api.get_api_resources, group=group, version=version
        )

    def is_healthy(self) -> bool:
        """
        Check if the Kubernetes API is accessible and healthy.

        Returns:
            bool: True if the API is healthy, False otherwise
        """
        try:
            self.core_api.get_api_resources()
            return True
        except Exception:
            return False

    def close(self) -> None:
        """
        Clean up the client resources.
        """
        if hasattr(self, "api_client"):
            self.api_client.close()


class CustomObjectMixin:
    """
    Mixin class providing common custom object operations.
    To be used with KubernetesClient-based classes.
    """

    def list_custom_objects(
        self,
        group: str,
        version: str,
        plural: str,
        namespace: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        List custom objects of a specific type.

        Args:
            group: The API group
            version: The API version
            plural: The plural name of the object type
            namespace: Optional namespace to list from
            **kwargs: Additional arguments to pass to the API call

        Returns:
            Dict containing the list of objects
        """
        if namespace:
            return self._make_api_call(
                self.custom_objects_api.list_namespaced_custom_object,
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                **kwargs,
            )
        return self._make_api_call(
            self.custom_objects_api.list_cluster_custom_object,
            group=group,
            version=version,
            plural=plural,
            **kwargs,
        )
