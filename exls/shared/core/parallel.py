from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Generic, List, TypeVar

from pydantic import BaseModel, Field
from typing_extensions import Optional

T_Input = TypeVar("T_Input")
T_Output = TypeVar("T_Output")


class _ExecutionResult(BaseModel, Generic[T_Input, T_Output]):
    item: T_Input = Field(..., description="The item that was processed")
    result: Optional[T_Output] = Field(
        default=None, description="The result of the processing"
    )
    error: Optional[Exception] = Field(
        default=None, description="The error that occurred"
    )

    @property
    def is_success(self) -> bool:
        return self.error is None


class ExecutionFailure(BaseModel, Generic[T_Input]):
    """Represents a failed execution for a specific item."""

    item: T_Input
    error: Exception
    message: str


class ParallelExecutionResult(BaseModel, Generic[T_Input, T_Output]):
    """Holds the results of a parallel execution, separating successes and failures."""

    successes: List[T_Output]
    failures: List[ExecutionFailure[T_Input]]

    @property
    def has_failures(self) -> bool:
        return len(self.failures) > 0


def execute_in_parallel(
    items: List[T_Input],
    func: Callable[[T_Input], T_Output],
    max_workers: int = 10,
) -> ParallelExecutionResult[T_Input, T_Output]:
    """
    Executes a function for each item in the list in parallel using a ThreadPoolExecutor.
    Captures exceptions for individual items so the entire batch doesn't fail.

    :param items: List of items to process.
    :param func: The function to apply to each item.
    :param max_workers: Maximum number of threads to use.
    :return: A structured result containing lists of successes and failures.
    """

    # Internal wrapper to catch exceptions and return a success/failure tuple
    def _safe_execute(item: T_Input) -> _ExecutionResult[T_Input, T_Output]:
        try:
            result: T_Output = func(item)
            return _ExecutionResult(item=item, result=result)
        except Exception as e:
            return _ExecutionResult(item=item, error=e)

    # Execute in parallel
    # map guarantees that results are returned in the same order as items
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results: List[_ExecutionResult[T_Input, T_Output]] = list[
            _ExecutionResult[T_Input, T_Output]
        ](executor.map(_safe_execute, items))

    # Sort results into successes and failures
    successes: List[T_Output] = []
    failures: List[ExecutionFailure[T_Input]] = []

    for result in results:
        if result.is_success:
            assert result.result is not None
            successes.append(result.result)
        else:
            assert result.error is not None
            failures.append(
                ExecutionFailure[T_Input](
                    item=result.item, error=result.error, message=str(result.error)
                )
            )

    return ParallelExecutionResult[T_Input, T_Output](
        successes=successes, failures=failures
    )
