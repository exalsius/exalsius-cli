from typing import List

import questionary

from exls.clusters.dtos import ClusterDTO
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO


def cluster_to_questionary_choice(cluster: ClusterDTO) -> questionary.Choice:
    """Convert a ClusterDTO to a questionary Choice."""
    return questionary.Choice(
        title=f"{cluster.name} - {cluster.cluster_status}",
        value=cluster.id,
    )


def clusters_to_questionary_choices(
    clusters: List[ClusterDTO],
) -> List[questionary.Choice]:
    """Convert a list of ClusterDTOs to questionary Choices."""
    return [cluster_to_questionary_choice(cluster) for cluster in clusters]


def template_to_questionary_choice(
    template: WorkspaceTemplateDTO,
) -> questionary.Choice:
    """Convert a WorkspaceTemplateDTO to a questionary Choice."""
    return questionary.Choice(
        title=f"{template.name} - {template.description}",
        value=template.name,
    )


def templates_to_questionary_choices(
    templates: List[WorkspaceTemplateDTO],
) -> List[questionary.Choice]:
    """Convert a list of WorkspaceTemplateDTOs to questionary Choices."""
    return [template_to_questionary_choice(template) for template in templates]
