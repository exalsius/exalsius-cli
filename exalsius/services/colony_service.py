from typing import Any

from exalsius.commands.colony.operations import (
    ColonyOperation,
    CreateColonyFromJobSumitOperation,
    WaitForColonyReadyOperation,
)


class ColonyService:
    def execute_operation(self, operation: ColonyOperation) -> Any:
        """
        Execute a colony operation.

        Args:
            operation (ColonyOperation): The operation to execute

        Returns:
            Any: The result of the operation
        """
        return operation.execute()

    def create_colony_from_job_submit(
        self,
        name: str,
        cloud: str,
        instance_type: str,
        region: str,
        price: float,
        parallelism: int,
    ) -> Any:
        """
        Create a colony from a job submit.
        """
        return CreateColonyFromJobSumitOperation(
            name, cloud, instance_type, region, price, parallelism
        ).execute()

    def wait_for_colony_to_be_ready(self, name: str) -> Any:
        """
        Wait for a colony to be ready.
        """
        return WaitForColonyReadyOperation(name).execute()
