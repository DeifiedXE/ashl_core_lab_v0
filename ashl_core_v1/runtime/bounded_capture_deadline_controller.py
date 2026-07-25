"""Atomic shared capture-deadline controller for Package 125."""

from __future__ import annotations

import threading

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.observation_window_types import (
    DEADLINE_EXTENSION_RESULT_SCHEMA_VERSION,
    DeadlineExtensionResult,
)


class BoundedCaptureDeadlineController:
    """Shared authoritative deadline for participating bounded lanes.

    The controller is intentionally small: it owns only event-time deadlines and
    makes compare-and-set extension decisions visible to all registered lanes.
    It never opens devices, changes sampling configuration, or selects focus.
    """

    def __init__(
        self,
        *,
        base_deadline_ns: int,
        hard_deadline_ns: int,
        participating_lanes: tuple[str, ...],
        maximum_extension_count: int = 1,
        maximum_total_extension_ns: int = 1_500_000_000,
    ) -> None:
        if base_deadline_ns <= 0:
            raise ValueError("base_deadline_ns must be positive")
        if hard_deadline_ns < base_deadline_ns:
            raise ValueError("hard_deadline_ns cannot precede base_deadline_ns")
        if maximum_extension_count < 0 or maximum_total_extension_ns < 0:
            raise ValueError("extension limits cannot be negative")
        lanes = tuple(str(item) for item in participating_lanes)
        if not lanes:
            raise ValueError("participating_lanes is required")
        self._lock = threading.Lock()
        self._base_deadline_ns = int(base_deadline_ns)
        self._current_deadline_ns = int(base_deadline_ns)
        self._hard_deadline_ns = int(hard_deadline_ns)
        self._maximum_extension_count = int(maximum_extension_count)
        self._maximum_total_extension_ns = int(maximum_total_extension_ns)
        self._extension_count = 0
        self._total_extension_ns = 0
        self._stop_requested = False
        self._stop_reason: str | None = None
        self._lane_deadlines = {lane: int(base_deadline_ns) for lane in lanes}

    def current_deadline_ns(self) -> int:
        with self._lock:
            return self._current_deadline_ns

    def lane_deadline_ns(self, lane: str) -> int:
        with self._lock:
            return self._lane_deadlines[str(lane)]

    def lane_deadlines(self) -> dict[str, int]:
        with self._lock:
            return dict(self._lane_deadlines)

    @property
    def extension_count(self) -> int:
        with self._lock:
            return self._extension_count

    @property
    def total_extension_ns(self) -> int:
        with self._lock:
            return self._total_extension_ns

    @property
    def stop_requested(self) -> bool:
        with self._lock:
            return self._stop_requested

    @property
    def stop_reason(self) -> str | None:
        with self._lock:
            return self._stop_reason

    def request_extension(
        self,
        *,
        expected_current_deadline_ns: int,
        extension_ns: int,
        policy_decision_id: str,
    ) -> DeadlineExtensionResult:
        with self._lock:
            failures: list[str] = []
            previous = self._current_deadline_ns
            requested = previous + int(extension_ns)
            status = "applied"
            cas = int(expected_current_deadline_ns) == previous
            if self._stop_requested:
                failures.append("operator_stop_requested")
                status = "operator_interrupted"
            if not cas:
                failures.append("stale_deadline")
                status = "stale_deadline"
            if extension_ns <= 0:
                failures.append("extension_ns_not_positive")
                status = "failed"
            if requested > self._hard_deadline_ns:
                failures.append("exceeds_hard_deadline")
                status = "exceeds_hard_deadline"
            if self._extension_count >= self._maximum_extension_count:
                failures.append("maximum_extension_count_exceeded")
                status = "failed"
            if self._total_extension_ns + int(extension_ns) > self._maximum_total_extension_ns:
                failures.append("maximum_total_extension_exceeded")
                status = "failed"

            applied = previous
            if not failures:
                self._current_deadline_ns = requested
                self._extension_count += 1
                self._total_extension_ns += int(extension_ns)
                for lane in self._lane_deadlines:
                    self._lane_deadlines[lane] = requested
                applied = requested
            return DeadlineExtensionResult(
                deadline_extension_result_id=stable_id("deadline_extension_result"),
                schema_version=DEADLINE_EXTENSION_RESULT_SCHEMA_VERSION,
                created_at=utc_now(),
                previous_deadline_ns=previous,
                requested_extension_ns=int(extension_ns),
                requested_new_deadline_ns=requested,
                applied_new_deadline_ns=applied,
                hard_deadline_ns=self._hard_deadline_ns,
                extension_count_after=self._extension_count,
                total_extension_ns_after=self._total_extension_ns,
                policy_decision_id=policy_decision_id,
                atomic_compare_and_set_succeeded=cas and not failures,
                all_lane_deadlines_updated=not failures and all(value == applied for value in self._lane_deadlines.values()),
                stop_requested=self._stop_requested,
                extension_status=status if failures else "applied",
                failure_reasons=tuple(failures),
            )

    def request_stop(self, reason: str) -> None:
        with self._lock:
            self._stop_requested = True
            self._stop_reason = str(reason)
