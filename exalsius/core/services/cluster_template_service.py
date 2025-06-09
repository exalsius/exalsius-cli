from typing import List, Optional, Tuple

from exalsius_api_client.models.cluster_template import ClusterTemplate

from exalsius.core.operations.cluster_template_operations import (
    ListClusterTemplatesOperation,
)
from exalsius.core.services.base import BaseService


class ClusterTemplateService(BaseService):
    def list_cluster_templates(self) -> Tuple[List[ClusterTemplate], Optional[str]]:
        return self.execute_operation(
            ListClusterTemplatesOperation(
                self.api_client,
            )
        )
