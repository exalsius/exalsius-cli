from typing import List, Optional, Tuple

from exalsius_api_client.models.cluster_template import ClusterTemplate

from exalsius.base.service import BaseServiceWithAuth
from exalsius.cluster_templates.operations import ListClusterTemplatesOperation


class ClusterTemplateService(BaseServiceWithAuth):
    def list_cluster_templates(self) -> Tuple[List[ClusterTemplate], Optional[str]]:
        return self.execute_operation(ListClusterTemplatesOperation(self.api_client))
