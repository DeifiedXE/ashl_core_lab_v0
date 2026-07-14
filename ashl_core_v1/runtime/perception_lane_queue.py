"""Bounded perception lane queues for Package 122."""

from __future__ import annotations

from dataclasses import dataclass

from ashl_core_v1.runtime.multimodal_perception_session_types import PerceptionBackpressureRecord, PerceptionDroppedSampleRecord, PerceptionLaneItem
from ashl_core_v1.runtime.perception_backpressure import build_backpressure_record, build_dropped_sample_record


@dataclass
class PerceptionLaneQueuePushResult:
    accepted: bool
    active_items: tuple[PerceptionLaneItem, ...]
    backpressure_records: tuple[PerceptionBackpressureRecord, ...]
    dropped_sample_records: tuple[PerceptionDroppedSampleRecord, ...]


class PerceptionLaneQueue:
    def __init__(self, *, session_id: str, source_kind: str, queue_depth_limit: int, drop_policy: str) -> None:
        if queue_depth_limit <= 0:
            raise ValueError("queue_depth_limit must be positive")
        self.session_id = session_id
        self.source_kind = source_kind
        self.queue_depth_limit = queue_depth_limit
        self.drop_policy = drop_policy
        self._items: list[PerceptionLaneItem] = []

    @property
    def items(self) -> tuple[PerceptionLaneItem, ...]:
        return tuple(self._items)

    def push(self, item: PerceptionLaneItem) -> PerceptionLaneQueuePushResult:
        if item.session_id != self.session_id:
            raise ValueError("lane item session_id mismatch")
        if item.source_kind != self.source_kind:
            raise ValueError(f"{self.source_kind} lane cannot accept {item.source_kind} item")
        backpressure: list[PerceptionBackpressureRecord] = []
        dropped: list[PerceptionDroppedSampleRecord] = []
        if len(self._items) < self.queue_depth_limit:
            self._items.append(item)
            self._items.sort(key=lambda value: value.session_relative_ns)
            return PerceptionLaneQueuePushResult(True, self.items, tuple(), tuple())
        if self.drop_policy in {"drop_oldest_with_trace", "drop_oldest_with_gap_trace"}:
            removed = self._items.pop(0)
            timeline_gap = self.drop_policy == "drop_oldest_with_gap_trace"
            dropped.append(
                build_dropped_sample_record(
                    item=removed,
                    reason_code="lane_queue_overflow",
                    drop_policy=self.drop_policy,
                    timeline_gap_created=timeline_gap,
                )
            )
            backpressure.append(
                build_backpressure_record(
                    session_id=self.session_id,
                    source_kind=self.source_kind,
                    queue_depth_before=self.queue_depth_limit,
                    queue_depth_limit=self.queue_depth_limit,
                    policy=self.drop_policy,
                    action_taken="drop_oldest",
                    affected_source_record_ids=(removed.primitive_record_id,),
                    source_trace_refs=removed.source_trace_refs,
                )
            )
            self._items.append(item)
            self._items.sort(key=lambda value: value.session_relative_ns)
            return PerceptionLaneQueuePushResult(True, self.items, tuple(backpressure), tuple(dropped))
        if self.drop_policy == "replace_older_pending_sample_with_trace":
            removed = self._items.pop(0)
            dropped.append(
                build_dropped_sample_record(
                    item=removed,
                    reason_code="lane_pending_sample_replaced",
                    drop_policy=self.drop_policy,
                    timeline_gap_created=False,
                )
            )
            backpressure.append(
                build_backpressure_record(
                    session_id=self.session_id,
                    source_kind=self.source_kind,
                    queue_depth_before=self.queue_depth_limit,
                    queue_depth_limit=self.queue_depth_limit,
                    policy=self.drop_policy,
                    action_taken="replace_pending",
                    affected_source_record_ids=(removed.primitive_record_id,),
                    source_trace_refs=removed.source_trace_refs,
                )
            )
            self._items.append(item)
            self._items.sort(key=lambda value: value.session_relative_ns)
            return PerceptionLaneQueuePushResult(True, self.items, tuple(backpressure), tuple(dropped))
        if self.drop_policy == "drop_new_with_trace":
            dropped.append(
                build_dropped_sample_record(
                    item=item,
                    reason_code="lane_queue_overflow_drop_new",
                    drop_policy=self.drop_policy,
                    timeline_gap_created=False,
                )
            )
            backpressure.append(
                build_backpressure_record(
                    session_id=self.session_id,
                    source_kind=self.source_kind,
                    queue_depth_before=self.queue_depth_limit,
                    queue_depth_limit=self.queue_depth_limit,
                    policy=self.drop_policy,
                    action_taken="drop_new",
                    affected_source_record_ids=(item.primitive_record_id,),
                    source_trace_refs=item.source_trace_refs,
                )
            )
            return PerceptionLaneQueuePushResult(False, self.items, tuple(backpressure), tuple(dropped))
        backpressure.append(
            build_backpressure_record(
                session_id=self.session_id,
                source_kind=self.source_kind,
                queue_depth_before=self.queue_depth_limit,
                queue_depth_limit=self.queue_depth_limit,
                policy=self.drop_policy,
                action_taken="stop_session",
                affected_source_record_ids=(item.primitive_record_id,),
                source_trace_refs=item.source_trace_refs,
            )
        )
        return PerceptionLaneQueuePushResult(False, self.items, tuple(backpressure), tuple(dropped))
