from unittest.mock import Mock, patch

import pytest

from exls.shared.core.polling import PollingTimeoutError, poll_until


def test_poll_until_success_immediately() -> None:
    """Test that poll_until returns immediately if the predicate is met."""
    fetcher = Mock(return_value="ready")
    predicate = Mock(return_value=True)

    result = poll_until(fetcher=fetcher, predicate=predicate)

    assert result == "ready"
    fetcher.assert_called_once()
    predicate.assert_called_once_with("ready")


@patch("exls.shared.core.polling.time")
def test_poll_until_success_after_retries(mock_time: Mock) -> None:
    """Test that poll_until retries and returns success."""
    # Setup time.time to always return start time so it doesn't timeout
    mock_time.time.return_value = 1000.0

    # Fetcher returns 'pending', then 'pending', then 'ready'
    fetcher = Mock(side_effect=["pending", "pending", "ready"])

    # Predicate returns True only for 'ready'
    def predicate_side_effect(val: str) -> bool:
        return val == "ready"

    predicate = Mock(side_effect=predicate_side_effect)

    result = poll_until(
        fetcher=fetcher, predicate=predicate, timeout_seconds=10, interval_seconds=1
    )

    assert result == "ready"
    assert fetcher.call_count == 3
    assert predicate.call_count == 3

    # Verify sleep was called twice (between attempts)
    assert mock_time.sleep.call_count == 2
    mock_time.sleep.assert_called_with(1)


@patch("exls.shared.core.polling.time")
def test_poll_until_timeout(mock_time: Mock) -> None:
    """Test that poll_until raises PollingTimeoutError on timeout."""
    # New implementation logic:
    # 1. start_time = time.time() -> returns 0
    # 2. fetcher() -> returns "pending"
    # 3. predicate() -> returns False
    # 4. Check timeout: time.time() (returns 0) - start_time (0) >= 5 (False)
    # 5. sleep(1)
    # 6. fetcher() -> returns "pending"
    # 7. predicate() -> returns False
    # 8. Check timeout: time.time() (returns 6) - start_time (0) >= 5 (True) -> break
    # 9. Raise PollingTimeoutError

    mock_time.time.side_effect = [0, 0, 6]

    fetcher = Mock(return_value="pending")
    predicate = Mock(return_value=False)

    with pytest.raises(PollingTimeoutError) as exc_info:
        poll_until(
            fetcher=fetcher, predicate=predicate, timeout_seconds=5, interval_seconds=1
        )

    assert str(exc_info.value) == "Operation timed out waiting for condition."

    # Should have tried twice based on the sequence above
    assert fetcher.call_count >= 1
    assert predicate.called
    mock_time.sleep.assert_called()


@patch("exls.shared.core.polling.time")
def test_poll_until_timeout_custom_message(mock_time: Mock) -> None:
    """Test that poll_until raises PollingTimeoutError with custom message."""
    mock_time.time.side_effect = [0, 10]

    fetcher = Mock(return_value="pending")
    predicate = Mock(return_value=False)
    custom_error = "Custom timeout error"

    with pytest.raises(PollingTimeoutError) as exc_info:
        poll_until(
            fetcher=fetcher,
            predicate=predicate,
            timeout_seconds=5,
            error_message=custom_error,
        )

    assert str(exc_info.value) == custom_error


def test_poll_until_typed_return() -> None:
    """Test type hinting behavior implicitly via execution."""
    fetcher = Mock(return_value=123)
    predicate = Mock(return_value=True)

    result: int = poll_until(fetcher=fetcher, predicate=predicate)
    assert result == 123


def test_poll_until_propagates_exceptions() -> None:
    """Test that exceptions from the fetcher are propagated immediately."""
    fetcher = Mock(side_effect=ValueError("Boom"))
    predicate = Mock()

    with pytest.raises(ValueError, match="Boom"):
        poll_until(fetcher=fetcher, predicate=predicate)


@patch("exls.shared.core.polling.time")
def test_poll_until_zero_timeout_checks_at_least_once(mock_time: Mock) -> None:
    """
    Test that a zero timeout results in at least one check before failure.
    """
    mock_time.time.return_value = 0
    fetcher = Mock(return_value="pending")
    predicate = Mock(return_value=False)

    with pytest.raises(PollingTimeoutError):
        poll_until(fetcher=fetcher, predicate=predicate, timeout_seconds=0)

    # Should be called exactly once
    fetcher.assert_called_once()
    predicate.assert_called_once()


@patch("exls.shared.core.polling.time")
def test_poll_until_interval_larger_than_timeout(mock_time: Mock) -> None:
    """
    Test behavior when interval is larger than timeout.
    Should check, sleep (full interval), then timeout.
    """
    # 1. start_time = 0
    # 2. fetcher -> pending
    # 3. time.time() (returns 0) - start >= timeout (5) -> False
    # 4. sleep(10)
    # 5. fetcher -> pending
    # 6. time.time() (returns 10) - start >= timeout (5) -> True -> break
    mock_time.time.side_effect = [0, 0, 10]

    fetcher = Mock(return_value="pending")
    predicate = Mock(return_value=False)

    with pytest.raises(PollingTimeoutError):
        poll_until(
            fetcher=fetcher, predicate=predicate, timeout_seconds=5, interval_seconds=10
        )

    # It should sleep 10 seconds even though timeout is 5
    # because sleep happens before the next check in the loop
    # actually sleep happens after the check for timeout fails.
    mock_time.sleep.assert_called_with(10)
