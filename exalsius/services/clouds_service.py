from typing import Any, List

from sky.clouds.cloud import Cloud

from exalsius.commands.clouds.operations import (
    CloudsOperation,
    ListEnabledCloudsOperation,
)


class CloudService:
    def execute_operation(self, operation: CloudsOperation) -> Any:
        """
        Execute a cloud operation.

        Args:
            operation (CloudOperation): The operation to execute

        Returns:
            Any: The result of the operation
        """
        return operation.execute()

    def get_enabled_clouds(self) -> List[str]:
        """
        Get a list of enabled cloud providers.
        This is a convenience method used by other services.
        """
        operation = ListEnabledCloudsOperation()
        clouds: list[Cloud] = self.execute_operation(operation)
        return [cloud._REPR for cloud in clouds]
