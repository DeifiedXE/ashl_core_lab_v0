"""Local output rate-limit policy for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.operator_console_types import (
    RATE_LIMIT_POLICY_SCHEMA_VERSION,
    OutputRateLimitPolicy,
)


def build_default_output_rate_limit_policy(
    *,
    minimum_interval_ms: int = 2000,
    maximum_queue_depth: int = 8,
) -> OutputRateLimitPolicy:
    return OutputRateLimitPolicy(
        policy_id="output_rate_limit_policy:default",
        schema_version=RATE_LIMIT_POLICY_SCHEMA_VERSION,
        minimum_interval_ms=minimum_interval_ms,
        maximum_queue_depth=maximum_queue_depth,
        overflow_policy="reject_new_with_log",
    )


def rate_limit_allows_dispatch(
    *,
    policy: OutputRateLimitPolicy,
    pending_output_count: int,
    latest_dispatch_age_ms: int | None,
) -> tuple[bool, str | None]:
    if pending_output_count >= policy.maximum_queue_depth:
        return False, "queue_depth_exceeded"
    if latest_dispatch_age_ms is not None and latest_dispatch_age_ms < policy.minimum_interval_ms:
        return False, "minimum_interval_not_elapsed"
    return True, None
