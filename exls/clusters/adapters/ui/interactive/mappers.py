from typing import List

import questionary

from exls.clusters.dtos import AllowedClusterTypesDTO, AllowedGpuTypesDTO, ClusterDTO
from exls.nodes.dtos import NodeDTO


def cluster_type_to_questionary_choice(
    cluster_type: AllowedClusterTypesDTO,
) -> questionary.Choice:
    return questionary.Choice(cluster_type.value, cluster_type)


def allowed_cluster_types_to_questionary_choices(
    default: AllowedClusterTypesDTO,
) -> List[questionary.Choice]:
    cluster_type_choices: List[questionary.Choice] = [
        cluster_type_to_questionary_choice(default)
    ]
    cluster_type_choices.extend(
        [
            cluster_type_to_questionary_choice(cluster_type)
            for cluster_type in AllowedClusterTypesDTO.values()
            if cluster_type != default
        ]
    )
    return cluster_type_choices


def gpu_type_to_questionary_choice(
    gpu_type: AllowedGpuTypesDTO,
) -> questionary.Choice:
    return questionary.Choice(gpu_type.value, gpu_type)


def allowed_gpu_types_to_questionary_choices(
    default: AllowedGpuTypesDTO,
) -> List[questionary.Choice]:
    gpu_type_choices: List[questionary.Choice] = [
        gpu_type_to_questionary_choice(default)
    ]
    gpu_type_choices.extend(
        [
            gpu_type_to_questionary_choice(gpu_type)
            for gpu_type in AllowedGpuTypesDTO.values()
            if gpu_type != default
        ]
    )
    return gpu_type_choices


def node_to_questionary_choice(
    node: NodeDTO,
) -> questionary.Choice:
    return questionary.Choice(
        title=f"{node.hostname} ({node.id[:8]}) - {node.node_status}",
        value=node.id,
    )


def nodes_to_questionary_choices(
    nodes: List[NodeDTO],
) -> List[questionary.Choice]:
    return [node_to_questionary_choice(node) for node in nodes]


def cluster_to_questionary_choice(cluster: ClusterDTO) -> questionary.Choice:
    return questionary.Choice(
        title=f"{cluster.name} ({cluster.id[:8]})",
        value=cluster.id,
    )


def clusters_to_questionary_choices(
    clusters: List[ClusterDTO],
) -> List[questionary.Choice]:
    return [cluster_to_questionary_choice(cluster) for cluster in clusters]
