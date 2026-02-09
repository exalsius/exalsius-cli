from datetime import datetime, timezone

import pytest

from exls.clusters.core.domain import (
    ClusterEvent,
    ClusterEventInvolvedObject,
)


def test_cluster_event_involved_object_creation() -> None:
    obj = ClusterEventInvolvedObject(
        kind="Pod",
        name="my-pod-abc123",
        namespace="default",
    )
    assert obj.kind == "Pod"
    assert obj.name == "my-pod-abc123"
    assert obj.namespace == "default"


def test_cluster_event_full_payload() -> None:
    event = ClusterEvent(
        watch_event_type="ADDED",
        namespace="kube-system",
        involved_object=ClusterEventInvolvedObject(
            kind="Node",
            name="worker-1",
            namespace="kube-system",
        ),
        type="Normal",
        reason="NodeReady",
        message="Node worker-1 status is now: NodeReady",
        timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
    )
    assert event.watch_event_type == "ADDED"
    assert event.namespace == "kube-system"
    assert event.involved_object.kind == "Node"
    assert event.involved_object.name == "worker-1"
    assert event.type == "Normal"
    assert event.reason == "NodeReady"
    assert event.message == "Node worker-1 status is now: NodeReady"
    assert event.timestamp is not None


def test_cluster_event_minimal_payload() -> None:
    event = ClusterEvent(
        watch_event_type="MODIFIED",
        namespace="default",
        involved_object=ClusterEventInvolvedObject(
            kind="Pod",
            name="test-pod",
            namespace="default",
        ),
    )
    assert event.watch_event_type == "MODIFIED"
    assert event.type is None
    assert event.reason is None
    assert event.message is None
    assert event.timestamp is None


def test_cluster_event_from_json() -> None:
    raw = {
        "watch_event_type": "ADDED",
        "namespace": "kube-system",
        "involved_object": {
            "kind": "Pod",
            "name": "coredns-abc123",
            "namespace": "kube-system",
        },
        "type": "Warning",
        "reason": "FailedScheduling",
        "message": "no nodes available to schedule pods",
    }
    event = ClusterEvent.model_validate(raw)
    assert event.watch_event_type == "ADDED"
    assert event.involved_object.kind == "Pod"
    assert event.involved_object.name == "coredns-abc123"
    assert event.type == "Warning"
    assert event.reason == "FailedScheduling"


def test_cluster_event_missing_required_field() -> None:
    with pytest.raises(Exception):
        ClusterEvent.model_validate(
            {
                "watch_event_type": "ADDED",
                # missing namespace and involved_object
            }
        )
