from typing import Any

from exalsius.commands.scan_prices.operations import ScanPricesOperation


class ScanPricesService:
    def execute_operation(self, operation: ScanPricesOperation) -> Any:
        """
        Execute a scan prices operation.

        Args:
            operation (ScanPricesOperation): The operation to execute

        Returns:
            Any: The result of the operation
        """
        return operation.execute()
