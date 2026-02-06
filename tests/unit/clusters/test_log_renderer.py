from datetime import datetime, timezone
from io import StringIO

from rich.console import Console

from exls.clusters.adapters.ui.display.log_renderer import ClusterLogRenderer
from exls.clusters.core.domain import ClusterEvent, ClusterEventInvolvedObject


def _make_console() -> tuple[Console, StringIO]:
    output = StringIO()
    console = Console(file=output, no_color=True, width=200)
    return console, output


def test_render_header() -> None:
    console, output = _make_console()
    renderer = ClusterLogRenderer(console=console)
    renderer.render_header("my-cluster")
    text = output.getvalue()
    assert "my-cluster" in text
    assert "Streaming logs" in text
    assert "Ctrl+C" in text


def test_render_event_normal() -> None:
    console, output = _make_console()
    renderer = ClusterLogRenderer(console=console)
    event = ClusterEvent(
        watch_event_type="ADDED",
        namespace="kube-system",
        involved_object=ClusterEventInvolvedObject(
            kind="Pod", name="coredns-abc", namespace="kube-system"
        ),
        type="Normal",
        reason="Scheduled",
        message="Successfully assigned pod",
        timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
    )
    renderer.render_event(event)
    text = output.getvalue()
    assert "10:30:00" in text
    assert "Normal" in text
    assert "Pod/coredns-abc" in text
    assert "Scheduled" in text
    assert "Successfully assigned pod" in text


def test_render_event_warning() -> None:
    console, output = _make_console()
    renderer = ClusterLogRenderer(console=console)
    event = ClusterEvent(
        watch_event_type="MODIFIED",
        namespace="default",
        involved_object=ClusterEventInvolvedObject(
            kind="Pod", name="failing-pod", namespace="default"
        ),
        type="Warning",
        reason="FailedScheduling",
        message="no nodes available",
    )
    renderer.render_event(event)
    text = output.getvalue()
    assert "Warning" in text
    assert "Pod/failing-pod" in text
    assert "FailedScheduling" in text


def test_render_event_multiline_message_flattened() -> None:
    console, output = _make_console()
    renderer = ClusterLogRenderer(console=console)
    event = ClusterEvent(
        watch_event_type="ADDED",
        namespace="default",
        involved_object=ClusterEventInvolvedObject(
            kind="ClusterSummary", name="my-summary", namespace="default"
        ),
        type="Normal",
        reason="sveltos",
        message="Resources deployed to cluster Capi\nteam-logsight/default-hetzna-logs",
    )
    renderer.render_event(event)
    text = output.getvalue()
    # The newline in the message should be replaced with a space
    assert (
        "Resources deployed to cluster Capi team-logsight/default-hetzna-logs" in text
    )
    # Verify it's a single line of output (header line only)
    lines = [line for line in text.strip().split("\n") if line.strip()]
    assert len(lines) == 1


def test_render_event_missing_optional_fields() -> None:
    console, output = _make_console()
    renderer = ClusterLogRenderer(console=console)
    event = ClusterEvent(
        watch_event_type="ADDED",
        namespace="default",
        involved_object=ClusterEventInvolvedObject(
            kind="Node", name="worker-1", namespace="default"
        ),
    )
    renderer.render_event(event)
    text = output.getvalue()
    assert "--------" in text
    assert "Node/worker-1" in text
