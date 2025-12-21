from typing import Any, Callable, Iterable, List
from unittest.mock import MagicMock, patch

from exls.shared.core.parallel import (
    ExecutionFailure,
    ParallelExecutionResult,
    execute_in_parallel,
)


class TestParallelExecution:
    """Tests for the execute_in_parallel function."""

    @patch("exls.shared.core.parallel.ThreadPoolExecutor")
    def test_execute_in_parallel_success(self, mock_executor_cls: MagicMock) -> None:
        """Test successful execution of all items."""
        # Setup the mock to execute synchronously
        mock_executor = mock_executor_cls.return_value
        mock_executor.__enter__.return_value = mock_executor

        # This side effect mimics the behavior of map but runs synchronously
        def sync_map(func: Callable[[Any], Any], items: Iterable[Any]) -> Iterable[Any]:
            return map(func, items)

        mock_executor.map.side_effect = sync_map

        # Test data
        items: List[int] = [1, 2, 3]

        def double(x: int) -> int:
            return x * 2

        # Execute
        result = execute_in_parallel(items, double, max_workers=2)

        # Assertions
        assert isinstance(result, ParallelExecutionResult)
        assert result.successes == [2, 4, 6]
        assert result.failures == []
        assert not result.has_failures

        # Verify executor usage
        mock_executor_cls.assert_called_with(max_workers=2)
        mock_executor.map.assert_called_once()

    @patch("exls.shared.core.parallel.ThreadPoolExecutor")
    def test_execute_in_parallel_all_failure(
        self, mock_executor_cls: MagicMock
    ) -> None:
        """Test execution where all items fail."""
        mock_executor = mock_executor_cls.return_value
        mock_executor.__enter__.return_value = mock_executor

        def sync_map(func: Callable[[Any], Any], items: Iterable[Any]) -> Iterable[Any]:
            return map(func, items)

        mock_executor.map.side_effect = sync_map

        items: List[str] = ["a", "b"]
        error_msg = "test error"

        def fail_always(x: str) -> str:
            raise ValueError(f"{error_msg} {x}")

        result = execute_in_parallel(items, fail_always)

        assert isinstance(result, ParallelExecutionResult)
        assert result.successes == []
        assert len(result.failures) == 2
        assert result.has_failures

        failure1 = result.failures[0]
        assert isinstance(failure1, ExecutionFailure)
        assert failure1.item == "a"
        assert isinstance(failure1.error, ValueError)
        assert str(failure1.error) == f"{error_msg} a"

        failure2 = result.failures[1]
        assert failure2.item == "b"

    @patch("exls.shared.core.parallel.ThreadPoolExecutor")
    def test_execute_in_parallel_mixed_results(
        self, mock_executor_cls: MagicMock
    ) -> None:
        """Test execution with mixed success and failure."""
        mock_executor = mock_executor_cls.return_value
        mock_executor.__enter__.return_value = mock_executor

        def sync_map(func: Callable[[Any], Any], items: Iterable[Any]) -> Iterable[Any]:
            return map(func, items)

        mock_executor.map.side_effect = sync_map

        items: List[int] = [1, 0, 2]  # 0 will cause division by zero

        def divide_ten_by(x: int) -> float:
            return 10.0 / x

        result = execute_in_parallel(items, divide_ten_by)

        assert len(result.successes) == 2
        assert 10.0 in result.successes
        assert 5.0 in result.successes

        assert len(result.failures) == 1
        assert result.failures[0].item == 0
        assert isinstance(result.failures[0].error, ZeroDivisionError)
        assert result.has_failures

    @patch("exls.shared.core.parallel.ThreadPoolExecutor")
    def test_execute_in_parallel_empty_list(self, mock_executor_cls: MagicMock) -> None:
        """Test execution with an empty list."""
        mock_executor = mock_executor_cls.return_value
        mock_executor.__enter__.return_value = mock_executor

        def sync_map(func: Callable[[Any], Any], items: Iterable[Any]) -> Iterable[Any]:
            return map(func, items)

        mock_executor.map.side_effect = sync_map

        def identity(x: Any) -> Any:
            return x

        result = execute_in_parallel([], identity)

        assert result.successes == []
        assert result.failures == []
        assert not result.has_failures

    def test_parallel_execution_result_model(self) -> None:
        """Test the ParallelExecutionResult model properties."""
        success_result: ParallelExecutionResult[int, int] = ParallelExecutionResult(
            successes=[1], failures=[]
        )
        assert not success_result.has_failures

        failure = ExecutionFailure(
            item="item", error=ValueError("oops"), message="oops"
        )
        fail_result: ParallelExecutionResult[str, int] = ParallelExecutionResult(
            successes=[], failures=[failure]
        )
        assert fail_result.has_failures

    def test_execute_in_parallel_real_executor(self) -> None:
        """
        Integration test using the real ThreadPoolExecutor.
        Ensures the code works with the actual standard library component.
        """
        items: List[int] = [1, 2, 3, 4, 5]

        def square(x: int) -> int:
            return x * x

        # Uses real threads (or 1 thread if strict serialization needed, but real class)
        result = execute_in_parallel(items, square, max_workers=2)

        assert result.successes == [1, 4, 9, 16, 25]
        assert not result.has_failures

    @patch("exls.shared.core.parallel.ThreadPoolExecutor")
    def test_execute_in_parallel_preserves_order(
        self, mock_executor_cls: MagicMock
    ) -> None:
        """Test that relative order of successes and failures is preserved."""
        mock_executor = mock_executor_cls.return_value
        mock_executor.__enter__.return_value = mock_executor

        # Mock sync execution
        def sync_map(func: Callable[[Any], Any], items: Iterable[Any]) -> Iterable[Any]:
            return map(func, items)

        mock_executor.map.side_effect = sync_map

        # Input: [Success, Fail, Success, Fail, Success]
        items: List[int] = [1, 2, 3, 4, 5]

        def odd_pass_even_fail(x: int) -> str:
            if x % 2 == 0:
                raise ValueError(f"Even {x}")
            return f"Success {x}"

        result = execute_in_parallel(items, odd_pass_even_fail)

        # Verify Successes are [1, 3, 5] in that exact order
        assert result.successes == ["Success 1", "Success 3", "Success 5"]

        # Verify Failures are [2, 4] in that exact order
        assert len(result.failures) == 2
        assert result.failures[0].item == 2
        assert result.failures[1].item == 4
