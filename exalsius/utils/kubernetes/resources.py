from typing import List, Optional, Tuple

from exalsius.utils.kubernetes.client import (
    CustomObjectMixin,
    KubernetesClient,
    KubernetesClientError,
)


class ResourceManager(KubernetesClient, CustomObjectMixin):
    """Manages Kubernetes resource operations."""

    def get_cluster_nodes(self, cluster_name: str) -> List[dict]:
        """
        Get nodes of a specific CAPI cluster.

        Args:
            cluster_name: Name of the CAPI cluster to get nodes for

        Returns:
            List of node objects matching the cluster name
        """
        response = self.list_custom_objects(
            group="cluster.x-k8s.io", version="v1beta1", plural="machines"
        )

        return [
            node
            for node in response.get("items", [])
            if node.get("spec", {}).get("clusterName") == cluster_name
        ]

    def get_colony_objects(self) -> Tuple[Optional[List[dict]], Optional[str]]:
        """
        Get all colony objects from the exalsius management cluster.

        Returns:
            Tuple[Optional[List[dict]], Optional[str]]: (colony_list, error_message)
            If successful, error_message will be None.
            If failed, colony_list will be None and error_message will contain the error.
        """
        try:
            response = self.list_custom_objects(
                group="infra.exalsius.ai", version="v1", plural="colonies"
            )
            return response.get("items", []), None

        except KubernetesClientError as e:
            if "404" in str(e):
                return (
                    None,
                    "Colony Custom Resource Definition (CRD) not found in the exalsius management cluster",
                )
            return None, str(e)

    def get_ddp_jobs(self) -> Tuple[Optional[List[dict]], Optional[str]]:
        """
        Get all DDP training jobs from the exalsius management cluster.

        Returns:
            Tuple[Optional[List[dict]], Optional[str]]: (jobs_list, error_message)
            If successful, error_message will be None.
            If failed, jobs_list will be None and error_message will contain the error.
        """
        try:
            response = self.list_custom_objects(
                group="training.exalsius.ai", version="v1", plural="ddpjobs"
            )
            return response.get("items", []), None

        except KubernetesClientError as e:
            if "404" in str(e):
                return (
                    None,
                    "Torch DDP training job (CRD) not found in the exalsius management cluster",
                )
            return None, str(e)

    def create_custom_object_from_dict(
        self, manifest_dict: dict, default_namespace: str = "default"
    ) -> dict:
        """
        Create a custom resource from a dictionary manifest.

        Args:
            manifest_dict: Dictionary containing the resource manifest
            default_namespace: Default namespace if not specified in manifest

        Returns:
            Dict containing the created resource

        Raises:
            KubernetesClientError: If creation fails
        """
        api_version = manifest_dict["apiVersion"]
        kind = manifest_dict["kind"]
        metadata = manifest_dict.get("metadata", {})

        if "/" in api_version:
            group, version = api_version.split("/", 1)
        else:
            group = ""
            version = api_version

        plural = kind.lower() + "s"
        if kind == "Colony":
            plural = "colonies"

        # Get namespace
        namespace = metadata.get("namespace", default_namespace)
        return self.custom_objects_api.create_namespaced_custom_object(
            group=group,
            version=version,
            plural=plural,
            body=manifest_dict,
            namespace=namespace,
        )

    def create_custom_object_from_yaml_file(
        self, manifest_path: str, default_namespace: str = "default"
    ) -> List[dict]:
        """
        Create custom resources from a YAML file.

        Args:
            manifest_path: Path to the YAML manifest file
            default_namespace: Default namespace if not specified in manifests

        Returns:
            List of created resources

        Raises:
            KubernetesClientError: If creation fails
        """
        import yaml

        with open(manifest_path, "r") as f:
            docs = list(yaml.safe_load_all(f))

        results = []
        for doc in docs:
            if not isinstance(doc, dict):
                continue
            result = self.create_custom_object_from_dict(doc, default_namespace)
            results.append(result)

        return results
