"""Tests for clusters app layer helpers."""

from typing import List
from unittest.mock import MagicMock

from exls.clusters.adapters.ui.display.log_renderer import ClusterLogRenderer
from exls.clusters.app import (
    _stream_logs_to_console,  # pyright: ignore[reportPrivateUsage]
)
from exls.clusters.core.domain import (
    ClusterEvent,
    ClusterEventInvolvedObject,
)


class _CloseableEventIterator:
    """Iterator that records when close() is called."""

    def __init__(self, events: List[ClusterEvent]) -> None:
        self._events = list(events)
        self.closed = False

    def __iter__(self) -> "_CloseableEventIterator":
        return self

    def __next__(self) -> ClusterEvent:
        if self._events:
            return self._events.pop(0)
        raise StopIteration

    def close(self) -> None:
        self.closed = True


def test_stream_logs_to_console_closes_iterator_on_normal_exit() -> None:
    """_stream_logs_to_console uses contextlib.closing so the iterator is closed."""
    event = ClusterEvent(
        watch_event_type="ADDED",
        namespace="default",
        involved_object=ClusterEventInvolvedObject(
            kind="Pod", name="test-pod", namespace="default"
        ),
    )
    iterator: _CloseableEventIterator = _CloseableEventIterator([event])
    renderer = MagicMock(spec=ClusterLogRenderer)

    _stream_logs_to_console(
        events=iterator,
        renderer=renderer,
        cluster_name="test-cluster",
        json_output=False,
    )

    assert iterator.closed is True


class _CloseableIteratorThatRaisesKeyboardInterrupt:
    """Iterator that yields one item then raises KeyboardInterrupt and records close()."""

    def __init__(self, event: ClusterEvent) -> None:
        self._event = event
        self._yielded = False
        self.closed = False

    def __iter__(self) -> "_CloseableIteratorThatRaisesKeyboardInterrupt":
        return self

    def __next__(self) -> ClusterEvent:
        if not self._yielded:
            self._yielded = True
            return self._event
        raise KeyboardInterrupt

    def close(self) -> None:
        self.closed = True


def test_stream_logs_to_console_closes_iterator_on_keyboard_interrupt() -> None:
    """_stream_logs_to_console closes the iterator even when KeyboardInterrupt is raised."""
    event = ClusterEvent(
        watch_event_type="ADDED",
        namespace="default",
        involved_object=ClusterEventInvolvedObject(
            kind="Pod", name="x", namespace="default"
        ),
    )
    iterator = _CloseableIteratorThatRaisesKeyboardInterrupt(event)
    renderer = MagicMock(spec=ClusterLogRenderer)

    try:
        _stream_logs_to_console(
            events=iterator,
            renderer=renderer,
            cluster_name="test-cluster",
            json_output=False,
        )
    except KeyboardInterrupt:
        pass  # Swallow KeyboardInterrupt so we can assert the iterator was closed

    assert iterator.closed is True
