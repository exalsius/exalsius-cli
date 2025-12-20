import time
from typing import Callable, TypeVar

from exls.shared.core.exceptions import ServiceError

T = TypeVar("T")


class PollingTimeoutError(ServiceError):
    pass


def poll_until(
    fetcher: Callable[[], T],
    predicate: Callable[[T], bool],
    timeout_seconds: int = 60,
    interval_seconds: int = 3,
    error_message: str = "Operation timed out waiting for condition.",
) -> T:
    """
    Generic polling utility.

    :param fetcher: Function to retrieve the current state (e.g., get_node).
    :param predicate: Function returning True if the condition is met (e.g., status == 'READY').
    :param timeout_seconds: Max time to wait.
    :param interval_seconds: Time to sleep between checks.
    :param error_message: Message to raise on timeout.
    :return: The final state object satisfying the predicate.
    """
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        result = fetcher()
        if predicate(result):
            return result
        time.sleep(interval_seconds)

    raise PollingTimeoutError(message=error_message)
