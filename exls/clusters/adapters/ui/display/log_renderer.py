from __future__ import annotations

from typing import Optional

from rich.console import Console

from exls.clusters.core.domain import ClusterEvent


class ClusterLogRenderer:
    def __init__(self, console: Optional[Console] = None):
        self._console: Console = console or Console()

    def render_header(self, cluster_name: str) -> None:
        self._console.print(
            f"Streaming logs for cluster [bold]{cluster_name}[/bold]..."
        )
        self._console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    def render_event(self, event: ClusterEvent) -> None:
        timestamp: str = (
            event.timestamp.strftime("%H:%M:%S") if event.timestamp else "--------"
        )
        event_type: str = event.type or ""
        kind: str = event.involved_object.kind
        name: str = event.involved_object.name
        reason: str = event.reason or ""
        message: str = (event.message or "").replace("\n", " ")

        style: str = "yellow" if event_type == "Warning" else "dim"

        self._console.print(
            f"[{style}]{timestamp}  {event_type:<8}  {kind}/{name}  {reason}  {message}[/{style}]"
        )
